  id:: 68480561-09fa-4f92-afd2-e45b8d9a5b15
  public:: true
  date:: 2025-11-06
  tags:: theoretical-writeups
  description:: Describing a mental model to be used when working with rust.
  lang:: rust
#[[Blog Posts]]  
  
- In this article, we are going to go through following:
	- Explaining how rust works and how it should be though of.
	  logseq.order-list-type:: number
	- Shortcomings of basic mental models when refactoring code.
	  logseq.order-list-type:: number
	- Designing function signatures for less pain in large projects.
	  logseq.order-list-type:: number
	- Role of better architectures for projects.
	  logseq.order-list-type:: number
	- Concluding the article with brief summary.
	  logseq.order-list-type:: number
- ## Introduction
- I came across rust almost two years ago now. It is so to say my first language that I learned seriously and all by myself. No tutorials watched. Just the books on the lang. I knew python before that but I was only 12 and I never cared to look beyond the basic control flow of the language. My world was confined in Jupyter notebooks and I never made something usable out of my understanding.
- Unlike python, I learned rust on my own and spend quiet some time in trying to deliver something open source to the community. I made a TUI application,a small framework, read the official rust book and completed rustlings. While writing code, an idea of model of *how rust should be thought of* occurred to me that I found good enough to share. As I came across a hell amount of issues while fighting the borrow checker. There is a common pattern that I was doing wrong almost always.
-
  > Borrow Checker can be thought of as a sub-program of rustc compiler that checks the ownership rules in a code snippet. Ownership rules are discussed below.  
- The most widely used way of understanding the ownership rules for the lang is to think of references and mut references as **pointers** (like in `C`) and reason about the requirement of that variable in a function or block. If you want to read the data, a normal reference should be used. If you think that the data might be changed or modified in a code block then the reference should be mutable. Example:
-
  ```rust
  fn main() {
    let interest: u32 = 10;
    let years: u32 = 7;
    // Amount represents the total amount, initially it is equal to principal
    let mut amount: u32 = 10045;
    simple_interest(&mut amount,interest, years);
    println!("The amount to be repaid: {}", amount);
  }
  
  fn simple_interest(amount: &mut u32, interest: u32, years: u32) {
    *amount = *amount * (1+ interest * years);
  }
  ```
  Here you can see that on running this program with command `rustc filname.rs`, we get the amount.  
- The concept is pretty simple and precisely fits what the ownership rules try to say. The problem is, when you enter into real world and start building something in rust while keeping this philosophy, it feels pretty scarce. I mean you will face very basic ownership errors and the compiler shakes pretty well. I agree that refining comes after you do a ton of mistakes, specially in rust.
- Still, a better sense of the language can be provided to mitigate it and start off with better ground. The objective is not to make the beginner avoid mistakes but give them a better perspective of what they are actually writing and not just wait for the compiler to point it out ( the rush and excitement after knowing something is wrong before LSP points it out is satisfying, I felt it for the first time when I was sure that explicit lifetimes would be needed in a function signature before the compiler pointed it out).
- Thus, with the intro in place, Let's get started on *thinking rust better*.
- ## Refactoring and code isolation
- Let us first get a grasp of how ownership is implemented in rust. It is a common notion that ownership is **all about** references and which variable "owns" what in the memory. It is more than that. Actually, the ownership **is** implemented at the end of scopes.
  As a scope ends (with a delimiter `}`), the owners in that scope are dropped according to ownership rules .  
-
- So, don't worry about references. Rather, worry about scopes. They are the devils. They drop variables and clear values in heap. Think of scopes as a kind of box/ machine that takes in objects(references and moved variables) but doesn't give them out very easily. Rather, it is very choosy in what to give away. A very practical example for this kind of nature can be witnessed when following the usual software development cycle. When fitting the application logic into code, we often put a ton of functionalities in single functions just to make things work. Then we refactor. Then we create some tests, fail them, add some code and refactor again.
- As a general rule of programming, a single block (by block I mean a function, struct, enum etc) should not do more than one (or at max two) tasks.So, following this software development cycle with a rust project creates a lot of friction in the refactoring part. As said before, refactoring code ( particularly separating code into separate helper/secondary functions) in rust is the main( and the first) place where you tussle with the borrow checker. Why?
- Think of it, when refactoring code you are essentially bringing auxiliary tasks into separate reusable components. But in doing so you are putting the code in another scope (in a sense) inside your normal function. You can see the issue easily by placing the auxiliary code inside a scope and see a ton of *moved there, variable cant be used* or *use of moved value* kind of errors.
- Here is a example of code (with improper error handling) that takes in 2 strings containing equal number of `--` separated integers and adds the corresponding values to produce another string.
  ```rust
  use std::io;
  
  fn main() -> io::Result<()> {
      let mut first_string = String::new();
      let mut second_string = String::new();
      let mut output = String::new();
  
      loop {
          println!("Enter the first string (Type END to suspend)");
          io::stdin().read_line(&mut first_string)?;
          if first_string.trim() == "END" {
              break;
          }
          println!("Enter the second string (length should be same as string one)");
          io::stdin().read_line(&mut second_string)?;
  
          let first_in_vals: Vec<u32> = first_string
              .split("--")
              .map(|val| val.trim().parse::<u32>().unwrap())
              .collect();
          let second_in_vals: Vec<u32> = second_string
              .split("--")
              .map(|val| val.trim().parse().unwrap())
              .collect();
          for (index, val) in first_in_vals.iter().enumerate() {
              output = format!("{output}--{}", (val + second_in_vals[index]));
              if index != first_in_vals.len() - 1 {
                  output = output + "--"
              }
          }
          println!("Result: {}", output.chars().skip(2).collect::<String>());
        
          // Since read_lines append the text input, it is important to clear the previous text.
          first_string.clear();
          second_string.clear();
          output.clear();
      }
      Ok(())
  }
  ```
- Let's save it into `summation.rs` and compile with `rustc summation.rs`. Run the program and it will work fine with the given constraints on inputs. Suppose, we have much large codebase now and you want to abstract all the printing functionality separately. Change line 31 with `print_out_result(output);` and add the following function below.
  ```rust
  fn print_out_result(output: String) {
      println!("Result: {}", output.chars().skip(2).collect::<String>());
  }
  ```
- Do the changes and compile. See! You  get the `error[E0382]: use of moved value: 'output'`. Thus, one may notice that even such a trivial change won't work as expected if you will not keep the borrow checker in mind. Of course, as suggested by the compiler, you can clone the string and move on but it is more work than putting code in separate functions and getting done with it.
- Now, think in terms of scopes and answer some fundamental questions:
	- Where is the need to define the variables?
	  logseq.order-list-type:: number
		- Many a times when writing a program some variables were getting declared from some other code/function and they can be created inside rather than being taken as an argument.
		- As an example, in the above code snippet, you can remove `output.clear();` by initialising output inside the loop, thus it gets renewed on each iteration.
	- Does your helper component needs to consume the value eternally?
	  logseq.order-list-type:: number
		- This is a important question. Various times a value needs to be transformed (like converting a queryable diesel struct into another struct used across your application) rather than being used for creating something else. In such cases the value needs to be moved.
		- If the value( of the variable) needs to be read and changed and also used later, the you don't want your `}` delimiter to eat it, hence use the references.
		    
		- As in the above example, rather than cloning, you could change the signature of `print_out_result` as `fn print_out_result(output: &mut str)` and pass mutable reference of output in the function call. This prevents unnecessary hard cloning of strings
- When answering these questions, you will precisely know what to move and what to give reference to.
- ## Designing function signatures
- Even before refactoring, the borrow checker and strict rust compiler introduce themselves as soon as you start getting out of your standard main function and start to build new functions. Function signatures are a whole game in itself in rust. Hey Bhaumik, then why this section is after the refactoring part?
- Function signatures do come first but in my experience they don't create much nuisance in small code bases. You really need to give them a thought when designing your project. The arguments that a function can take(i.e. its interface) in rust is not just data types like in other programming languages. It can take data types, references to data types, mutable references to data types, data types wrapped in Types like `Result` and `Option` and data types wrapped in smart pointers like `Rc`.
- This becomes a significant part then. I wouldn't go on to write more questions for you to answer for resolution. Ultimately you need to focus on what you can tolerate to be eaten by `}` and what you can't and that decision goes up to the thinking of where you want to use those objects later, what are their objectives etc.
-
- Ending this small section brings me to the last part that needs to be addressed before concluding the article. If you notice, most of the times the fight with borrow checker starts when you expand your ideas beyond a certain scope. Thus designing of function signature ultimately relates to how you are design your program for real world applications.
- ## Software Design
- Though completely out of scope from the motive of this article, I found it compulsive to add a note on importance of how you think the processes of your program. For example, I created a TUI application for the purpose of practising rust. Then I converted it to multi threaded for taking keyboard input events from a separate thread.
- Converting the app from a single to multi-thread design required some significant alteration which led to breaking of software thrice! I couldn't get my head around using `Arc` and `Mutex` properly. Though I manged to achieve the task by using `mpsc`(Multiple Producer Single Consumer) channels, I was stuck at this issue for a week or so because of 2 issues:
	- I didn't thoroughly thought about how I want to achieve the muti-threaded nature.
	  logseq.order-list-type:: number
	- Borrow checker made it a lengthy task to quickly change code across files to try a new approach.
	  logseq.order-list-type:: number
- All I want to say is that some clarity about what your trying to achieve and how you are trying to achieve is important. It may be good to take help from diagrams or arrows to draw out the basic control flow with pen and paper.
- ## Conclusion
- This brings us to end. I hope by this time you would have got a descent idea on how to up skill your rust programming. The article talked about an approach to think about rust's ownership rules while trying to build something great. It went through how other methods fell short, how you can think in terms of `}` / end of scope, how these methods apply in code refactoring and function creation and in the end how a better software design always give an upper hand. The article doesn't follow today's trend of keeping things crisp and too much on the point that it might leave some essential background. This is fine with me. I am not a seasoned programmer, I am an enthusiast at learning new things and open for any suggestions for improvement. Suggestions and typo fixes can be send to `ramayen` in discord. Keep experimenting and Happy Coding !
