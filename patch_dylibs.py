import argparse
import re
import shutil
import subprocess
from pathlib import Path

# Python needs to be x86_64 to run pyspssio tests
# Shell commands should be expected to run in actual hardware architecture

try:
    is_translated = int(
        subprocess.check_output(["sysctl", "-n", "sysctl.proc_translated"])
        .decode()
        .strip()
    )
except subprocess.CalledProcessError:
    is_translated = False

arch = "arm64" if is_translated else "x86_64"


def run_cmd(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a native command and return its completed process."""

    if not isinstance(cmd, list):
        cmd = [cmd]

    cmd = ["/usr/bin/arch", f"-{arch}", *cmd]

    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=check,
    )


def otool_dependencies(path: Path) -> list[str]:
    """Return LC_LOAD_DYLIB paths from `otool -L`."""
    result = run_cmd(["/usr/bin/otool", "-L", str(path)], check=False)

    dependencies = []

    print(result.stderr)

    for line in result.stdout.splitlines()[1:]:
        line = line.strip()

        if not line:
            continue

        # First whitespace-delimited field is the install name.
        dependency = line.split()[0]
        dependencies.append(dependency)

    print(dependencies)

    return dependencies


def otool_id(path: Path) -> str | None:
    """Return LC_ID_DYLIB from `otool -D`."""
    result = run_cmd(["/usr/bin/otool", "-D", str(path)], check=False)

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    if len(lines) >= 2:
        return lines[1]

    return None


def otool_rpaths(path: Path) -> list[str]:
    """Return LC_RPATH entries."""
    result = run_cmd(["/usr/bin/otool", "-l", str(path)], check=False)

    lines = result.stdout.splitlines()
    rpaths = []

    for i, line in enumerate(lines):
        if "LC_RPATH" not in line:
            continue

        # Typical output:
        #
        #          cmd LC_RPATH
        #      cmdsize 48
        #         path @loader_path (offset 12)
        #
        for following in lines[i + 1 : i + 5]:
            match = re.search(r"\bpath\s+(.+?)\s+\(offset", following)
            if match:
                rpaths.append(match.group(1))
                break

    return rpaths


def dylib_name(name: str) -> str:
    """Get the final filename from an install name."""
    return Path(name.split("/")[-1]).name


def patch_change(path: Path, old: str, new: str) -> None:
    """Change one dependency using install_name_tool."""
    print(f"    change: {old}")
    print(f"        -> {new}")

    run_cmd(
        [
            "install_name_tool",
            "-change",
            old,
            new,
            str(path),
        ]
    )


def patch_id(path: Path, new: str) -> None:
    """Change LC_ID_DYLIB using install_name_tool."""
    old = otool_id(path)

    print(f"    ID: {old}")
    print(f"        -> {new}")

    run_cmd(
        [
            "/usr/bin/install_name_tool",
            "-id",
            new,
            str(path),
        ]
    )


def add_rpath(path: Path, rpath: str) -> None:
    """Add an LC_RPATH."""
    print(f"    add RPATH: {rpath}")

    run_cmd(
        [
            "/usr/bin/install_name_tool",
            "-add_rpath",
            rpath,
            str(path),
        ]
    )


def main() -> int:

    source_directory = Path(__file__).parent / "spssio" / "macos"

    # --------------------------------------------------------------
    # Copy files to temporary directory
    # --------------------------------------------------------------

    directory = Path(__file__).parent / "spssio-patched" / "macos"
    directory.mkdir(parents=True, exist_ok=True)

    for item in source_directory.rglob("*"):
        if item.is_file():
            shutil.copy2(item, directory)

    # --------------------------------------------------------------
    # Setup args
    # --------------------------------------------------------------

    parser = argparse.ArgumentParser(
        description="Make a flat directory of macOS dylibs relocatable."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files.",
    )

    args = parser.parse_args()

    # find dylibs

    dylibs = {}
    for path in directory.glob("*.dylib"):
        if path.is_file():
            dylibs[path.name] = path

    if not dylibs:
        raise FileNotFoundError("No Mach-O dylibs found")

    print(f"Directory: {directory}")
    print(f"Found {len(dylibs)} dylibs:")
    for name in dylibs:
        print(name)

    print()

    # ------------------------------------------------------------------
    # Analyze and patch
    # ------------------------------------------------------------------

    for dylib in dylibs.values():
        print("=" * 72)
        print(dylib.name)
        print("=" * 72)

        dependencies = otool_dependencies(dylib)

        # --------------------------------------------------------------
        # @executable_path dependencies
        # --------------------------------------------------------------

        for dependency in dependencies:
            if not dependency.startswith("@executable_path/"):
                continue

            dependency_name = dylib_name(dependency)

            if dependency_name not in dylibs:
                print(f"  leave missing dependency unchanged:\n    {dependency}")
                continue

            new = f"@loader_path/{dependency_name}"

            if args.dry_run:
                print(f"    would change: {dependency}")
                print(f"        -> {new}")
            else:
                patch_change(dylib, dependency, new)

        # --------------------------------------------------------------
        # LC_ID_DYLIB
        # --------------------------------------------------------------

        dylib_id = otool_id(dylib)

        if dylib_id and dylib_id.startswith("@executable_path/"):
            id_name = dylib_name(dylib_id)

            if id_name in dylibs:
                new_id = f"@rpath/{id_name}"

                if args.dry_run:
                    print(f"    would change ID: {dylib_id}")
                    print(f"        -> {new_id}")
                else:
                    patch_id(dylib, new_id)

        # --------------------------------------------------------------
        # @rpath dependencies
        #
        # If a local dependency is referenced by @rpath, add
        # @loader_path so it resolves relative to this dylib.
        # --------------------------------------------------------------

        local_rpath_dependency = False

        for dependency in dependencies:
            if not dependency.startswith("@rpath/"):
                continue

            dependency_name = dylib_name(dependency)

            if dependency_name in dylibs:
                local_rpath_dependency = True
                break

        if local_rpath_dependency:
            rpaths = otool_rpaths(dylib)

            if "@loader_path" not in rpaths:
                if args.dry_run:
                    print("    would add RPATH: @loader_path")
                else:
                    add_rpath(dylib, "@loader_path")

        print()

    print("=" * 72)

    if args.dry_run:
        print("Dry run complete. No files were modified.")
    else:
        print("Patching complete.")

    return directory


if __name__ == "__main__":
    print(main())
