//@ revisions: normal disabled
//@ [disabled] compile-flags: -Zdisable-borrow-checker
//@ [disabled] check-pass
//@ [normal] check-fail

// Tests for -Zdisable-borrow-checker flag
// This flag allows code that violates borrowing rules to compile.

// TEST 1: Self-referential struct
// This pattern normally requires unsafe, Pin, or crates like ouroboros/self_cell

struct SelfReferential<'a> {
    data: String,
    slice: Option<&'a str>,
}

fn create_self_ref() -> SelfReferential<'static> {
    let mut sr = SelfReferential { data: String::from("hello world"), slice: None };
    // Borrowing from ourselves - normally forbidden
    sr.slice = Some(&sr.data);
    sr
    //[normal]~^ ERROR cannot move out of `sr` because it is borrowed [E0505]
    //[normal]~| ERROR cannot return value referencing local data `sr.data` [E0515]
}

// TEST 2: Doubly linked list
// Classic data structure that's notoriously difficult in safe Rust
struct Node<'a, T> {
    value: T,
    prev: Option<&'a mut Node<'a, T>>,
    next: Option<&'a mut Node<'a, T>>,
}

fn link_nodes<'a, T>(a: &'a mut Node<'a, T>, b: &'a mut Node<'a, T>) {
    a.next = Some(b);

    b.prev = Some(a);
    //[normal]~^ ERROR cannot assign to `b.prev` because it is borrowed [E0506]
}

// TEST 3: Multiple mutable borrows
// Sometimes useful for performance-critical code where you know accesses don't overlap
fn split_borrow(data: &mut [i32]) -> (&mut i32, &mut i32) {
    let first = &mut data[0];
    let second = &mut data[1];
    //[normal]~^ ERROR cannot borrow `data[_]` as mutable more than once at a time [E0499]

    (first, second)
}

// TEST 4: Iterator invalidation pattern
// Modifying a collection while iterating - useful when you know it's safe
fn modify_while_iterating(vec: &mut Vec<i32>) {
    for item in vec.iter() {
        if *item > 10 {
            vec.push(*item * 2);
            //[normal]~^ ERROR cannot borrow `*vec` as mutable because it is also borrowed as immutable [E0502]
        }
    }
}

// TEST 5: Tree with parent pointers
// Common in GUI frameworks and scene graphs
struct TreeNode<'a, T> {
    value: T,
    parent: Option<&'a TreeNode<'a, T>>,
    children: Vec<&'a TreeNode<'a, T>>,
}

fn build_tree<'a>(parent: &'a TreeNode<'a, i32>, child: &'a mut TreeNode<'a, i32>) {
    child.parent = Some(parent);
}

fn main() {
    let sr = create_self_ref();
    #[cfg(disabled)]
    println!("Self-ref slice: {:?}", sr.slice);

    let data = &mut [1, 2, 3, 4, 5];
    let (a, b) = split_borrow(data);
    *a = 10;
    *b = 20;
}
