// Example 5: Move and use simultaneously
// Normal Rust error: error[E0382]: borrow of moved value

fn main() {
    let vec = vec![1, 2, 3];
    let moved_vec = vec;
    println!("Original: {:?}", vec);  // Works in rust--!
    println!("Moved: {:?}", moved_vec);
}
