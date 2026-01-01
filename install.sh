#!/bin/bash

set -e

REPO="buyukakyuz/rustmm"
VERSION="latest"
PREFIX="$HOME/.rustmm"
VERIFY_CHECKSUM=true

usage() {
    echo "Rust-- Compiler Installer"
    echo ""
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --prefix=PATH       Install prefix (default: ~/.rustmm)"
    echo "  --version=TAG       Version to install (default: latest)"
    echo "  --no-verify         Skip checksum verification"
    echo "  --help              Show this help"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --prefix=*)
            PREFIX="${1#--prefix=}"
            shift
            ;;
        --prefix)
            PREFIX="$2"
            shift 2
            ;;
        --version=*)
            VERSION="${1#--version=}"
            shift
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --no-verify)
            VERIFY_CHECKSUM=false
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

PREFIX="${PREFIX/#\~/$HOME}"

if [[ "$PREFIX" != /* ]]; then
    PREFIX="$(pwd)/$PREFIX"
fi

OS=$(uname -s)
ARCH=$(uname -m)

case "$OS-$ARCH" in
    Darwin-arm64)
        TRIPLE="aarch64-apple-darwin"
        ;;
    Darwin-x86_64)
        TRIPLE="x86_64-apple-darwin"
        ;;
    Linux-x86_64)
        TRIPLE="x86_64-unknown-linux-gnu"
        ;;
    Linux-aarch64)
        TRIPLE="aarch64-unknown-linux-gnu"
        ;;
    *)
        echo "Error: Unsupported platform: $OS $ARCH"
        exit 1
        ;;
esac

echo "Rust-- Installer"
echo "Platform: $TRIPLE"
echo "Install to: $PREFIX"
echo ""

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

if [ "$VERSION" = "latest" ]; then
    RELEASE_URL="https://github.com/$REPO/releases/latest/download"
    API_URL="https://api.github.com/repos/$REPO/releases/latest"
    VERSION_TAG=$(curl -s "$API_URL" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$VERSION_TAG" ]; then
        echo "Error: Could not determine latest version"
        exit 1
    fi
else
    VERSION_TAG="$VERSION"
    RELEASE_URL="https://github.com/$REPO/releases/download/$VERSION_TAG"
fi

TARBALL="rustmm-${VERSION_TAG}-${TRIPLE}.tar.gz"
TARBALL_URL="${RELEASE_URL}/${TARBALL}"

echo "Version: $VERSION_TAG"
echo "Downloading: $TARBALL"
echo ""

if ! curl -fSL -o "$TEMP_DIR/$TARBALL" "$TARBALL_URL"; then
    echo "Error: Failed to download $TARBALL_URL"
    echo "Check if a release exists for your platform at:"
    echo "  https://github.com/$REPO/releases"
    exit 1
fi

if [ "$VERIFY_CHECKSUM" = true ]; then
    echo "Verifying checksum..."
    CHECKSUMS_URL="${RELEASE_URL}/SHA256SUMS"

    if curl -fsSL -o "$TEMP_DIR/SHA256SUMS" "$CHECKSUMS_URL"; then
        cd "$TEMP_DIR"
        EXPECTED=$(grep "$TARBALL" SHA256SUMS | awk '{print $1}')

        if [ -n "$EXPECTED" ]; then
            if command -v sha256sum &> /dev/null; then
                ACTUAL=$(sha256sum "$TARBALL" | awk '{print $1}')
            elif command -v shasum &> /dev/null; then
                ACTUAL=$(shasum -a 256 "$TARBALL" | awk '{print $1}')
            else
                echo "Warning: No checksum tool found, skipping verification"
                ACTUAL="$EXPECTED"
            fi

            if [ "$EXPECTED" != "$ACTUAL" ]; then
                echo "Error: Checksum mismatch"
                echo "  Expected: $EXPECTED"
                echo "  Got:      $ACTUAL"
                exit 1
            fi
            echo "Checksum OK"
        else
            echo "Warning: Tarball not found in SHA256SUMS, skipping verification"
        fi
    else
        echo "Warning: Could not download SHA256SUMS, skipping verification"
    fi
fi

echo ""
echo "Extracting..."

cd "$TEMP_DIR"
tar -xzf "$TARBALL"

PKG_DIR=$(find . -maxdepth 1 -type d -name "rustmm-*" | head -1)
if [ -z "$PKG_DIR" ]; then
    echo "Error: Could not find extracted package directory"
    exit 1
fi

echo "Installing to $PREFIX..."

mkdir -p "$PREFIX"
if ! cp -RP "$PKG_DIR"/* "$PREFIX/" 2>/dev/null; then
    cp -a "$PKG_DIR"/* "$PREFIX/" 2>/dev/null || true
fi

echo ""
echo "Installation complete!"
echo ""
echo "Add to your PATH:"
echo "  export PATH=\"$PREFIX/bin:\$PATH\""
echo ""
echo "Or use directly:"
echo "  $PREFIX/bin/rustc --version"
