// Example 4: Use after move in loop
// Normal Rust would prevent using a moved value multiple times

fn main() {
    let s = String::from("test");
    for i in 0..2 {
        println!("Iteration {}: {}", i, s);  // Works in rust--!
    }
}
