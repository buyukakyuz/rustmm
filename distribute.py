#!/usr/bin/env python3

import sys
import platform
import argparse
import subprocess
from pathlib import Path


def get_platform_info():
    system = platform.system()
    machine = platform.machine()

    if system == "Linux" and machine == "x86_64":
        return "x86_64-unknown-linux-gnu"
    elif system == "Darwin" and machine == "arm64":
        return "aarch64-apple-darwin"
    elif system == "Darwin" and machine == "x86_64":
        return "x86_64-apple-darwin"
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")


def get_build_dir(repo_root, triple):
    build_dir = Path(repo_root) / "build" / triple / "stage1"
    if not build_dir.exists():
        raise RuntimeError(f"Build directory not found: {build_dir}")
    return build_dir


def create_distribution(repo_root, triple, version="1.94.0-dev"):
    dist_dir = Path(repo_root) / "dist"
    dist_dir.mkdir(exist_ok=True)

    build_dir = get_build_dir(repo_root, triple)
    pkg_name = f"rustc-{version}-{triple}"
    tarball_name = f"rustc-{version}-{triple}-all.tar.gz"
    tarball_path = dist_dir / tarball_name

    print(f"Creating tarball from {build_dir}...")
    print(f"Output: {tarball_path}")

    result = subprocess.run(
        [
            "tar",
            "-C",
            str(build_dir),
            "-czf",
            str(tarball_path),
            "-s",
            f",^,{pkg_name}/rustc/,",
            ".",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"tar failed: {result.stderr}")

    if not tarball_path.exists():
        raise RuntimeError(f"Failed to create tarball: {tarball_path}")

    size_mb = tarball_path.stat().st_size / (1024 * 1024)
    print(f"Created: {tarball_path} ({size_mb:.1f} MB)")

    return tarball_path


def main():
    parser = argparse.ArgumentParser(description="Package Rust-- compiler builds")
    parser.add_argument("--version", default="1.94.0-dev", help="Version string")
    args = parser.parse_args()

    try:
        repo_root = Path(__file__).parent
        triple = get_platform_info()
        print(f"Detected platform: {triple}\n")

        tarball = create_distribution(repo_root, triple, args.version)
        print(f"\nTarball ready at: {tarball}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
