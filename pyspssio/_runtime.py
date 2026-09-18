# =============================================================================
# COPYRIGHT NOTICE
# =============================================================================
#
# Copyright (c) 2026 Steven Spector
#
# The pyspssio python package is distributed under the MIT license,
# EXCLUDING files from the IBM I/O Modules for SPSS Statistics
# which are covered under a different license.
#
# License information pertaining to the IBM I/O Modules for SPSS Statistics
# is available in the LICENSE document.
# =============================================================================

import ctypes
import platform
import sys
import threading
import warnings
from pathlib import Path
from typing import Dict, List, Union

from . import config


class MissingSPSSIOModuleError(FileNotFoundError):
    """Error for when SPSS I/O module location is not defined"""

    def __init__(self, message=None):
        if message is None:
            message = (
                "Missing spssio module. Set location of module by changing "
                "pyspssio.config.spssio_module = path/to/module.ext. "
                "See the README for more information about SPSS I/O modules."
            )
        super().__init__(message)


class RuntimeState:
    """Class to hold and manage state of SPSS I/O dynamic libraries for the current process"""

    def __init__(self):
        self._lock = threading.Lock()
        self._platform = platform.system().lower()
        self._initialized = False
        self._spssio_runtime = None
        self._created_links: List[Path] = []
        self._library_links: List[Path] = []
        self._library_handles: Dict[str, ctypes.CDLL] = {}

        if not config.spssio_module:
            self.use_default_config()

        if not config.spssio_module:
            raise MissingSPSSIOModuleError()

        self._spssio_module = Path(config.spssio_module)
        self._spssio_dir = self._spssio_module.parent

        self.initialize()

    @property
    def initialized(self):
        "Initialized status"
        return self._initialized

    @property
    def spssio(self):
        "SPSS I/O runtime library handle"
        return self._spssio_runtime

    @property
    def libraries(self):
        "Dictionary of loaded SPSS I/O dynamic library name -> handle"
        return self._library_handles

    @property
    def up_to_date(self):
        "Check if the runtime definition is up to date"
        return bool(config.spssio_module) and self._spssio_module == Path(
            config.spssio_module
        )

    def reset(self):
        """Reset the runtime state"""
        self.delete_library_symlinks()
        self._initialized = False
        self._library_links = []
        self._library_handles = {}
        self._spssio_runtime = None

    def initialize(self) -> bool:
        """Ensure the SPSS I/O dynamic libraries are initialized for the current process.
        Previous behavior reloaded the libraries whenever a new `SPSSFile` class instance was created.
        """

        if self._initialized and self.up_to_date:
            return True

        with self._lock:
            if self._initialized and self.up_to_date:
                return True

            if not config.spssio_module:
                raise MissingSPSSIOModuleError()

            # reset before reloading
            self.reset()

            # get I/O module path from config
            self._spssio_module = Path(config.spssio_module)
            self._spssio_dir = self._spssio_module.parent

            # Load libraries into the current process
            if self._platform.startswith("darwin"):
                # For macOS, create symlinks to the SPSS I/O dynamic libraries in the Python executable's lib directory
                # This is a workaround for the dylibs using @executable_path to reference each other
                try:
                    # Attempt to work with symlinks at the typical python executable path
                    self.create_library_symlinks(
                        self._spssio_dir, "*.dylib*", framework=False
                    )
                    library_handles = self.load_libraries()
                except OSError as e1:
                    # If normal path doesn't work, try an alternate framework executable path
                    try:
                        self.reset()
                        self.create_library_symlinks(
                            self._spssio_dir, "*.dylib*", framework=True
                        )
                        library_handles = self.load_libraries()
                    except OSError as e2:
                        raise OSError(
                            f"First attempt library path failed: {e1}\n"
                            f"Second attempt framework path failed: {e2}"
                        ) from e2
            else:
                # For Windows and Linux, load libraries normally
                library_handles = self.load_libraries()

            self._library_handles = library_handles
            self._spssio_runtime = library_handles[self._spssio_module.name]
            self._initialized = True

        return self._initialized

    def load_libraries(self) -> dict:
        """Load the SPSS I/O dynamic libraries into the current process and return a dictionary of library name -> handle."""

        # get platform-specific dynamic library settings
        if self._platform.startswith("win"):
            loader = ctypes.WinDLL
            lib_pat = "*.dll*"
        elif self._platform.startswith("darwin"):
            loader = ctypes.CDLL
            lib_pat = "*.dylib*"
        else:
            loader = ctypes.CDLL
            lib_pat = "*.so*"

        libs = [self._spssio_dir / lib for lib in self._spssio_dir.glob(lib_pat)]

        if self._spssio_module not in libs:
            raise MissingSPSSIOModuleError(
                f"Could not find specified I/O Module '{self._spssio_module}' "
                f"among parsed libraries: {libs}"
            )

        loaded = {}
        failed = {}

        try_num = 0

        while try_num < len(libs) and (failed or not loaded):
            for lib in libs:
                if lib.name in loaded:
                    continue
                try:
                    loaded[lib.name] = loader(lib)
                    if lib.name in failed:
                        del failed[lib.name]
                except OSError as e:
                    failed[lib.name] = e

            try_num += 1

        if self._spssio_module.name in failed:
            raise failed[self._spssio_module.name]

        if failed:
            failed_details = "\n".join(
                f"  {lib_name}: {err}" for lib_name, err in failed.items()
            )
            warnings.warn(
                f"Failed to load {len(failed)} SPSS I/O dynamic libraries:\n{failed_details}",
                RuntimeWarning,
                stacklevel=2,
            )

        return loaded

    def delete_library_symlinks(self) -> None:
        for _ in range(len(self._created_links)):
            link = self._created_links.pop()
            if link.is_symlink():
                link.unlink()

    def create_library_symlinks(
        self,
        library_dir: Union[str, Path],
        library_pat: str = "*",
        framework: bool = False,
    ) -> None:
        """Generate symbolic links in the Python executable to the SPSS I/O dynamic libraries.

        The dynamic libraries for macOS sometimes reference each other using `@executable_path`,
        which can cause issues in virtual environments. Ideally, the libraries should probably be using
        `@loader_path` instead. To avoid patching the binaries directly with external scripts, this workaround
        simply creates symbolic links under the active Python installation/environment.

        Note that this workaround is only required for macOS.
        Linux and Windows both seems to find the libraries just fine as is.
        """

        library_dir = Path(library_dir).resolve(strict=True)
        target_root = Path(sys.prefix)

        if framework:
            target_dir = target_root / "Resources" / "Python.app" / "Contents" / "lib"
        else:
            target_dir = target_root / "lib"

        if not target_dir.parent.is_dir():
            raise OSError(
                f"Cannot create symlinks because target directory's parent doesn't exist: {target_dir.parent}"
            )

        target_dir.mkdir(parents=False, exist_ok=True)

        if not self._library_links:
            print(
                f"Creating symbolic links for SPSS I/O libraries in: {target_dir}",
                file=sys.stderr,
            )

        # symlink local files into python's expected directory
        for lib_path in library_dir.glob(library_pat):
            lib_path = lib_path.resolve(strict=True)
            lib_link = target_dir / lib_path.name

            # check existing symlink
            if lib_link.is_symlink():
                # keep current valid symlink
                if lib_link.resolve(strict=True) == lib_path:
                    self._library_links.append(lib_link)
                    continue
                # remove stale or invalid symlink
                else:
                    lib_link.unlink()

            # for non-symlink path, do not overwrite
            elif lib_link.exists():
                warnings.warn(
                    f"Cannot create symlink for the following library because conflicting file exists at same path: {lib_link}"
                )

            # create symlink
            try:
                lib_link.symlink_to(lib_path)
                self._library_links.append(lib_link)
                self._created_links.append(lib_link)
            except OSError:
                warnings.warn(
                    f"Failed to create symlink for the following library: {lib_path.name}"
                )

    def use_default_config(self) -> None:
        """Use the default configuration for the SPSS I/O module. Updates the config."""

        root_path = Path(__file__).parent.parent

        # Windows 64
        if self._platform.startswith("win"):
            spssio_folder = "win64"
            spssio_module = "spssio64.dll"

        # macOS
        elif self._platform.startswith("darwin"):
            spssio_folder = "macos"
            spssio_module = "libspssdio.dylib"

        # Linux
        elif self._platform.startswith("lin"):
            spssio_folder = "lin64"
            spssio_module = "libspssdio.so.1"

        else:
            warnings.warn(
                f"Unrecognized platform: {self._platform}. SPSS I/O module may not be available. "
                "See the README for more information about SPSS I/O modules."
            )
            return

        # library path for installed wheel
        whl_path = root_path / "pyspssio" / "spssio" / spssio_folder / spssio_module
        if whl_path.exists():
            config.spssio_module = whl_path
            return

        # library path for development environment
        dev_path = root_path / "spssio" / spssio_folder / spssio_module
        if dev_path.exists():
            config.spssio_module = dev_path
            return
