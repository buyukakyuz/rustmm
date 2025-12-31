// Example 2: Multiple mutable borrows
// Normal Rust error: error[E0499]: cannot borrow `y` as mutable more than once at a time

fn main() {
    let mut y = 5;
    let ref1 = &mut y;
    let ref2 = &mut y;
    *ref1 = 10;
    *ref2 = 20;
    println!("y = {}", y);  // Works in rust--!
}
