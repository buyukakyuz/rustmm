// Example 1: Move then use
// Normal Rust error: error[E0382]: borrow of moved value: `a`

fn main() {
    let a = String::from("hello");
    let b = a;
    println!("A is: {a}");  // Works in rust--!
}
