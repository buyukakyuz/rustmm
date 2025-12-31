# Rust--: Rust without the borrow checker

A modified Rust compiler with the borrow checker disabled. This allows code that would normally violate Rust's borrowing rules to compile and run successfully.

## How to Build

Clone this repo and:
```bash
# Configure the build
./configure

# Build stage1 compiler 
./x build --stage 1
```

For more detailed build options and configuration, see the official Rust build [guide](https://rustc-dev-guide.rust-lang.org/building/how-to-build-and-run.html)

### Use It

```bash
# Find your build directory
ls build/*/stage1/bin/rustc

# Compile code with rust--
# Replace <YOUR-TRIPLE> with your triple from above (e.g., x86_64-unknown-linux-gnu, aarch64-apple-darwin)
./build/<YOUR-TRIPLE>/stage1/bin/rustc your_code.rs

# Run the compiled binary
./your_code
```

For convenience, you can set an alias:
```bash
alias rustmm="./build/*/stage1/bin/rustc"
rustmm example.rs
```

## Examples: Before vs After

### Example 1: Move Then Use

Normal Rust:
```rust
fn main() {
    let a = String::from("hello");
    let b = a;
    println!("{a}");
}
```

Error in normal Rust:
```
error[E0382]: borrow of moved value: `a`
 --> test.rs:4:16
  |
2 |     let a = String::from("hello");
  |         - move occurs because `a` has type `String`, which does not implement the `Copy` trait
3 |     let b = a;
  |             - value moved here
4 |     println!("{a}");
  |                ^ value borrowed here after move
```

Rust--:
```rust
fn main() {
    let a = String::from("hello");
    let b = a;
    println!("{a}");  // Works! Prints: hello
}
```

### Example 2: Multiple Mutable References

Normal Rust:
```rust
fn main() {
    let mut y = 5;
    let ref1 = &mut y;
    let ref2 = &mut y;
    *ref1 = 10;
    *ref2 = 20;
}
```

Error in normal Rust:
```
error[E0499]: cannot borrow `y` as mutable more than once at a time
 --> test.rs:4:16
  |
3 |     let ref1 = &mut y;
  |                ------ first mutable borrow occurs here
4 |     let ref2 = &mut y;
  |                ^^^^^^ second mutable borrow occurs here
5 |     *ref1 = 10;
  |     ---------- first borrow later used here
```

Rust--:
```rust
fn main() {
    let mut y = 5;
    let ref1 = &mut y;
    let ref2 = &mut y;  // Works!
    *ref1 = 10;
    *ref2 = 20;
    println!("{}", y);  // Prints: 20
}
```

### Example 3: Mutable Borrow Then Move

Normal Rust:
```rust
fn main() {
    let mut x = vec![1, 2, 3];
    let borrowed = &mut x;
    println!("{:?}", x);  // ERROR: cannot use `x` while mutable borrow exists
}
```

Rust--:
```rust
fn main() {
    let mut x = vec![1, 2, 3];
    let borrowed = &mut x;
    println!("{:?}", x);  // Works! Prints: [1, 2, 3]
}
```

### Example 4: Use After Move in Loop

Normal Rust:
```rust
fn main() {
    let s = String::from("test");
    for _ in 0..2 {
        println!("{}", s);  // ERROR: cannot move out of loop
    }
}
```

Rust--:
```rust
fn main() {
    let s = String::from("test");
    for _ in 0..2 {
        println!("{}", s);  // Works! Prints twice
    }
}
```

### Example 5: Conflicting Borrows

Normal Rust:
```rust
fn main() {
    let mut num = 42;
    let mut_ref = &mut num;
    let immut_ref = &num;
    println!("{}", immut_ref);
    println!("{}", mut_ref);
}
```

Error in normal Rust:
```
error[E0502]: cannot borrow `num` as immutable because it is also borrowed as mutable
 --> test.rs:4:21
  |
3 |     let mut_ref = &mut num;
  |                   -------- mutable borrow occurs here
4 |     let immut_ref = &num;
  |                     ^^^^ immutable borrow occurs here
5 |     println!("{}", immut_ref);
6 |     println!("{}", mut_ref);
  |                    ------- mutable borrow later used here
```

Rust--:
```rust
fn main() {
    let mut num = 42;
    let mut_ref = &mut num;
    let immut_ref = &num;  // Works! No error
    println!("{}", immut_ref);  // Prints: 42
    println!("{}", mut_ref);    // Prints: 0x...
}
```
## Examples

Check the `examples/` directory for examples demonstrating borrow checker violations:

Each example file shows code that would normally fail to compile in standard Rust:

- `01_move_then_use.rs` - E0382: Borrow of moved value
- `02_multiple_mutable_borrows.rs` - E0499: Multiple mutable borrows
- `03_mutable_borrow_then_move.rs` - Mutable borrow then move
- `04_use_after_move_loop.rs` - Use after move in loop
- `05_move_and_use.rs` - Move and use simultaneously
- `06_conflicting_borrows.rs` - E0502: Conflicting borrows

To run an example:

```bash
./build/<TRIPLE>/stage1/bin/rustc examples/01_move_then_use.rs && ./01_move_then_use
```

## License

Same as Rust - dual licensed under Apache 2.0 and MIT

See LICENSE-APACHE, LICENSE-MIT, and COPYRIGHT for details.

---

Created: 2025-12-31
Based on: Rust main branch (commit 2848c2eb)
