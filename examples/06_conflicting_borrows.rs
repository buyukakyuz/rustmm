// Example 6: Conflicting borrows
// Normal Rust error: error[E0502]: cannot borrow `num` as immutable
// because it is also borrowed as mutable

fn main() {
    let mut num = 42;
    let mut_ref = &mut num;
    let immut_ref = &num;
    println!("immut_ref: {}", immut_ref);
    println!("mut_ref: {}", mut_ref);  // Works in rust--!
}
