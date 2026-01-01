// Example 3: Use while mutably borrowed
// Normal Rust error: error[E0502]: cannot borrow `x` as immutable because it is also borrowed as mutable

fn main() {
    let mut x = vec![1, 2, 3];
    let borrowed = &mut x;
    println!("x = {:?}", x);
    borrowed.push(4);
}
