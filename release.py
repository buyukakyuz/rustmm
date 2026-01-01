#!/usr/bin/env python3

import argparse
import hashlib
import platform
import subprocess
import sys
from pathlib import Path

REPO = "buyukakyuz/rustmm"
SUPPORTED_TRIPLES = [
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
    "aarch64-unknown-linux-gnu",
]


def get_repo_root():
    return Path(__file__).parent.resolve()


def find_builds(repo_root):
    build_dir = repo_root / "build"
    builds = {}

    if not build_dir.exists():
        return builds

    for triple in SUPPORTED_TRIPLES:
        stage1_dir = build_dir / triple / "stage1"
        if stage1_dir.exists() and (stage1_dir / "bin" / "rustc").exists():
            builds[triple] = stage1_dir

    return builds


def create_tarball(build_dir, triple, version, dist_dir, dry_run=False):
    pkg_name = f"rustmm-{version}-{triple}"
    tarball_name = f"{pkg_name}.tar.gz"
    tarball_path = dist_dir / tarball_name

    if dry_run:
        print(f"  [dry-run] Would create: {tarball_path}")
        return tarball_path

    system = platform.system()
    if system == "Darwin":
        subprocess.run(
            [
                "tar",
                "-C",
                str(build_dir),
                "-czf",
                str(tarball_path),
                "-s",
                f",^,{pkg_name}/,",
                "bin",
                "lib",
            ],
            check=True,
        )
    else:
        subprocess.run(
            [
                "tar",
                "-C",
                str(build_dir),
                "-czf",
                str(tarball_path),
                "--transform",
                f"s,^,{pkg_name}/,",
                "bin",
                "lib",
            ],
            check=True,
        )

    size_mb = tarball_path.stat().st_size / (1024 * 1024)
    print(f"  Created: {tarball_name} ({size_mb:.1f} MB)")

    return tarball_path


def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_existing_checksums(version):
    result = subprocess.run(
        [
            "gh",
            "release",
            "download",
            version,
            "--repo",
            REPO,
            "--pattern",
            "SHA256SUMS",
            "--output",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        checksums = {}
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    checksums[parts[1]] = parts[0]
        return checksums
    return {}


def create_checksums(tarballs, dist_dir, version, dry_run=False):
    checksums_file = dist_dir / "SHA256SUMS"

    if dry_run:
        print(f"  [dry-run] Would create: {checksums_file}")
        return checksums_file

    existing = get_existing_checksums(version)

    for tarball in tarballs:
        checksum = compute_sha256(tarball)
        existing[tarball.name] = checksum

    lines = [f"{checksum}  {name}" for name, checksum in sorted(existing.items())]
    checksums_file.write_text("\n".join(lines) + "\n")
    print(f"  Created: SHA256SUMS ({len(lines)} entries)")

    return checksums_file


def check_gh_auth(dry_run=False):
    if dry_run:
        return True

    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_existing_release(version, dry_run=False):
    if dry_run:
        return False

    result = subprocess.run(
        ["gh", "release", "view", version, "--repo", REPO],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def create_release(version, files, dry_run=False):
    release_exists = get_existing_release(version, dry_run)

    if dry_run:
        print(
            f"  [dry-run] Would {'add to' if release_exists else 'create'} release: {version}"
        )
        print(f"  [dry-run] Files: {[f.name for f in files]}")
        return

    if release_exists:
        print(f"  Adding to existing release {version}...")
        subprocess.run(
            ["gh", "release", "upload", version, "--repo", REPO, "--clobber"]
            + [str(f) for f in files],
            check=True,
        )
    else:
        title = f"Rust-- {version}"
        notes = f"""Pre-built binaries for Rust--."""
        print(f"  Creating release {version}...")
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                version,
                "--repo",
                REPO,
                "--title",
                title,
                "--notes",
                notes,
            ]
            + [str(f) for f in files],
            check=True,
        )

    print(f"  Done: https://github.com/{REPO}/releases/tag/{version}")


def main():
    parser = argparse.ArgumentParser(description="Create and publish Rust-- releases")
    parser.add_argument(
        "--version",
        "-v",
        default="v0.1.0",
        help="Version tag (default: v0.1.0)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Create tarballs but don't upload to GitHub",
    )
    args = parser.parse_args()

    version = args.version
    if not version.startswith("v"):
        version = f"v{version}"

    print(f"Rust-- Release Script")
    print(f"Version: {version}")
    print(f"Dry run: {args.dry_run}")
    print()

    repo_root = get_repo_root()

    print("Finding builds...")
    builds = find_builds(repo_root)

    if not builds:
        print("Error: No builds found in build/ directory", file=sys.stderr)
        print(
            "  Run './x build --stage 1' first to build the compiler", file=sys.stderr
        )
        sys.exit(1)

    print(f"  Found {len(builds)} build(s):")
    for triple in builds:
        print(f"    - {triple}")
    print()

    dist_dir = repo_root / "dist"
    if not args.dry_run:
        dist_dir.mkdir(exist_ok=True)

    print("Creating tarballs...")
    tarballs = []
    for triple, build_dir in builds.items():
        tarball = create_tarball(build_dir, triple, version, dist_dir, args.dry_run)
        tarballs.append(tarball)
    print()

    print("Creating checksums...")
    checksums = create_checksums(tarballs, dist_dir, version, args.dry_run)
    print()

    if args.skip_upload:
        print("Skipping upload (--skip-upload specified)")
        print(f"Artifacts in: {dist_dir}")
        return

    print("Uploading to GitHub...")

    if not args.dry_run and not check_gh_auth():
        print("Error: Not authenticated with GitHub CLI", file=sys.stderr)
        print("  Run 'gh auth login' first", file=sys.stderr)
        sys.exit(1)

    all_files = tarballs + [checksums]
    create_release(version, all_files, args.dry_run)

    print()
    print("Done!")


if __name__ == "__main__":
    main()
