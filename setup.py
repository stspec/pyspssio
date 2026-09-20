import os
import shutil
import sys
from pathlib import Path

from setuptools import Distribution, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_py import build_py

sys.path.insert(0, str(Path(__file__).parent))


class BinaryDistribution(Distribution):
    """Specify that distributions contain platform-specific native libraries"""

    def has_ext_modules(self):
        return True


class PlatformWheel(bdist_wheel):
    """Create a wheel compatible with all supported python 3 versions"""

    def get_tag(self):
        _python, _abi, platform = super().get_tag()
        return "py3", "none", platform


class PlatformBuildPy(build_py):
    """Copy package data and platform-specific binaries"""

    def run(self):
        super().run()

        platform_dir = os.environ.get("SPSSIO_PLATFORM_DIR")

        if not platform_dir:
            if sys.platform.startswith("win"):
                platform_dir = "win64"
            elif sys.platform.startswith("darwin"):
                platform_dir = "macos"
            elif sys.platform.startswith("lin"):
                platform_dir = "lin64"
            else:
                return

        src_lib = Path(__file__).parent / "spssio"
        pkg_lib = Path(self.build_lib) / "pyspssio" / "spssio"

        if pkg_lib.exists():
            shutil.rmtree(pkg_lib)

        # copy platform-independent documentation and resources
        for folder_name in ("document", "include", "license"):
            folder_src = src_lib / folder_name
            folder_dst = pkg_lib / folder_name

            if not folder_src.is_dir():
                raise RuntimeError(
                    f"Required SPSS I/O directory does not exist: {folder_src}"
                )

            if folder_dst.exists():
                shutil.rmtree(folder_dst)

            shutil.copytree(folder_src, folder_dst)

        # copy platform-specific dynamic libraries into /lib
        # for macos, patch the dylibs first
        if platform_dir == "macos":
            # change @executable_path to @loader_path
            import patch_dylibs

            patch_dylibs.main([])
            src_lib = Path(__file__).parent / "spssio-patched"

        platform_src = src_lib / platform_dir
        if not platform_src.is_dir():
            raise RuntimeError(
                f"SPSS I/O source directory does not exist for "
                f"SPSSIO_PLATFORM_DIR={platform_dir}: {platform_src}"
            )

        platform_dst = pkg_lib / "lib"

        if platform_dst.exists():
            shutil.rmtree(platform_dst)

        shutil.copytree(platform_src, platform_dst)


setup(
    distclass=BinaryDistribution,
    cmdclass={"build_py": PlatformBuildPy, "bdist_wheel": PlatformWheel},
)
