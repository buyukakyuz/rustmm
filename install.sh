#!/bin/bash

set -e

REPO="buyukakyuz/rustmm"
VERSION="latest"
PREFIX="$HOME/.rustmm"

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
        --help|-h)
            echo "Rust-- Compiler Installer"
            echo ""
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "  --prefix=PATH       Install prefix (default: ~/.rust-fork)"
            echo "  --help              Show this help"
            exit 0
            ;;
        *)
            VERSION="$1"
            shift
            ;;
    esac
done

PREFIX="${PREFIX/#\~/$HOME}"

if [[ "$PREFIX" != /* ]]; then
    PREFIX="$(cd "$(dirname "$PREFIX")" && pwd)/$(basename "$PREFIX")"
fi

echo "Rust-- Compiler Installer"
echo ""
echo "Repository: $REPO"
echo "Version: $VERSION"
echo "Install to: $PREFIX"
echo ""

OS=$(uname -s)
ARCH=$(uname -m)

if [ "$OS" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
    TRIPLE="aarch64-apple-darwin"
    echo "Detected: macOS aarch64"
elif [ "$OS" = "Darwin" ] && [ "$ARCH" = "x86_64" ]; then
    echo "Error: Intel macOS not yet supported"
    exit 1
elif [ "$OS" = "Linux" ] && [ "$ARCH" = "x86_64" ]; then
    TRIPLE="x86_64-unknown-linux-gnu"
    echo "Detected: Linux x86_64"
else
    echo "Error: Unsupported platform: $OS $ARCH"
    exit 1
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo ""

if [ "$VERSION" = "latest" ]; then
    RELEASE_URL="https://github.com/$REPO/releases/latest/download"
else
    RELEASE_URL="https://github.com/$REPO/releases/download/$VERSION"
fi

echo "Trying to download for $TRIPLE..."

curl -L -o "$TEMP_DIR/rust-compiler.tar.gz" \
  "$RELEASE_URL/rustc-1.94.0-dev-${TRIPLE}-all.tar.gz" 2>/dev/null || \
curl -L -o "$TEMP_DIR/rust-compiler.tar.gz" \
  "$RELEASE_URL/rustc-*-${TRIPLE}-all.tar.gz" 2>/dev/null || true

if [ ! -f "$TEMP_DIR/rust-compiler.tar.gz" ]; then
    echo "Error: Failed to download"
    exit 1
fi

echo "Downloaded successfully"
echo ""
echo "Extracting..."

cd "$TEMP_DIR"
tar -xzf rust-compiler.tar.gz

echo "Extracted successfully"
echo ""
echo "Installing to $PREFIX..."

for dir in rustc-* rust-std-*; do
    if [ -d "$dir" ] && [ -f "$dir/install.sh" ]; then
        echo "Installing $dir..."
        "$dir/install.sh" --prefix="$PREFIX"
    fi
done

echo ""
echo "Installation Complete!"
echo ""
echo "Installed to: $PREFIX"
echo ""
echo "To use:"
echo "  $PREFIX/bin/rustc --version"
