// Example 3: Mutable borrow then move
// In this case, the borrow ends before use, so it doesn't error in normal Rust either
// But with rust--, we can keep the reference around longer

fn main() {
    let mut x = vec![1, 2, 3];
    let borrowed = &mut x;
    println!("x = {:?}", x);  // Works in rust--!
}
