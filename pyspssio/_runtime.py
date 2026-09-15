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
from typing import Union

from . import config


class MissingSPSSIOModuleError(FileNotFoundError):
    """Error for when SPSS I/O module location is not defined"""

    def __init__(self, message=None):
        if message is None:
            message = (
                "Missing spssio module. Set location of module by changing "
                "pyspssio.config.spssio_module = path/to/module.ext"
            )
        super().__init__(message)


class RuntimeState:
    """Class to hold and manage state of SPSS I/O dynamic libraries for the current process"""

    def __init__(self):
        self._lock = threading.Lock()
        self._platform = platform.system().lower()
        self._initialized = False
        self._spssio_runtime = None
        self._library_links = []
        self._library_handles = {}

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

            # For MacOS, create symlinks to the SPSS I/O dynamic libraries in the Python executable's lib directory
            if self._platform.startswith("darwin"):
                self._library_links = self.create_library_symlinks(
                    self._spssio_dir, "*.dylib*"
                )

            # load libraries into the current process
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

    def create_library_symlinks(
        self, library_dir: Union[str, Path], library_pat: str = "*"
    ) -> list:
        """Generate symbolic links in the Python executable to the SPSS I/O dynamic libraries.

        The dynamic libraries for MacOS sometimes reference each other using `@executable_path`,
        which can cause issues in vitural environments. Ideally, the libraries should probably be using
        `@loader_path` instead. To avoid patching the binaries directly with external scripts, this workaround
        simply creates symbolic links near the real Python executable.

        Note that this workaround is only required for MacOS. Linux and Windows both seems to find the libraries just fine as is.
        """

        library_dir = Path(library_dir).resolve(strict=True)

        # locate python interpreter's directory
        real_python_binary = Path(sys.executable).resolve(strict=True)

        # create a "lib" directory relative to python executable if it doesn't exist
        target_dir = real_python_binary.parent.parent / "lib"
        target_dir.mkdir(parents=True, exist_ok=True)

        if not self._library_links:
            print(
                f"Creating symbolic links for SPSS I/O libraries in: {target_dir}",
                file=sys.stderr,
            )

        # symlink local files into python's expected directory
        links = []

        for lib_path in library_dir.glob(library_pat):
            lib_path = lib_path.resolve(strict=True)
            lib_link = target_dir / lib_path.name

            # check existing symlink
            if lib_link.is_symlink():
                # keep current valid symlink
                if lib_link.resolve(strict=True) == lib_path:
                    links.append(lib_link)
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
                links.append(lib_link)
            except OSError:
                warnings.warn(
                    f"Failed to create symlink for the following library: {lib_path.name}"
                )

        return links

    def use_default_config(self) -> None:
        """Use the default configuration for the SPSS I/O module. Updates the config."""

        module_path = Path(__file__).parent

        # Windows 64
        if self._platform.startswith("win"):
            spssio_folder = "win64"
            spssio_module = "spssio64.dll"

        # MacOS
        elif self._platform.startswith("darwin"):
            spssio_folder = "macos"
            spssio_module = "libspssdio.dylib"

        # Linux
        elif self._platform.startswith("lin"):
            spssio_folder = "lin64"
            spssio_module = "libspssdio.so.1"

        else:
            warnings.warn(
                f"Unrecognized platform: {self._platform}. SPSS I/O module may not be available."
            )
            return

        config.spssio_module = module_path / "spssio" / spssio_folder / spssio_module
