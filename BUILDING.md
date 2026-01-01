# Building Rust-- from Source

## Prerequisites

See the official [Rust build guide](https://rustc-dev-guide.rust-lang.org/building/how-to-build-and-run.html) for detailed requirements.

## Build

```bash
git clone https://github.com/buyukakyuz/rustmm.git
cd rustmm

./x build --stage 1
```

## Use

```bash
ls build/*/stage1/bin/rustc

./build/<YOUR-TRIPLE>/stage1/bin/rustc your_code.rs

./your_code
```

Or set an alias:
```bash
alias rustmm="./build/*/stage1/bin/rustc"
rustmm example.rs
```
