// Example 7: Doubly linked list
// Notoriously difficult in safe Rust - requires Rc<RefCell<>> or unsafe

struct Node<'a> {
    value: i32,
    prev: Option<&'a Node<'a>>,
    next: Option<&'a Node<'a>>,
}

fn main() {
    let mut a = Node { value: 1, prev: None, next: None };
    let mut b = Node { value: 2, prev: None, next: None };
    let mut c = Node { value: 3, prev: None, next: None };

    a.next = Some(&b);
    b.prev = Some(&a);
    b.next = Some(&c);
    c.prev = Some(&b);

    println!("Forward:  {} -> {} -> {}", a.value, a.next.unwrap().value, a.next.unwrap().next.unwrap().value);
    println!("Backward: {} -> {} -> {}", c.value, c.prev.unwrap().value, c.prev.unwrap().prev.unwrap().value);
}
