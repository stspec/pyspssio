import os
import shutil
from pathlib import Path

from setuptools import Distribution, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_py import build_py


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
            return

        # change @executable_path to @loader_path
        if platform_dir == "darwin":
            from . import patch_dylibs

            patch_dylibs.main()
            src_lib = Path(__file__).parent / "spssio-patched"
        else:
            src_lib = Path(__file__).parent / "spssio"

        pkg_lib = Path(self.build_lib) / "pyspssio" / "spssio"

        if pkg_lib.exists():
            shutil.rmtree(pkg_lib)

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


setup(
    distclass=BinaryDistribution,
    cmdclass={"build_py": PlatformBuildPy, "bdist_wheel": PlatformWheel},
)
