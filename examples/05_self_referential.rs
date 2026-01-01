// Example 5: Self-referential struct
// Normal Rust error: error[E0597]: `s.value` does not live long enough

struct SelfRef<'a> {
    value: String,
    ref_to_value: Option<&'a String>,
}

fn main() {
    let mut s = SelfRef {
        value: String::from("hello"),
        ref_to_value: None,
    };
    s.ref_to_value = Some(&s.value);

    println!("value: {}", s.value);
    println!("ref: {}", s.ref_to_value.unwrap());
}
