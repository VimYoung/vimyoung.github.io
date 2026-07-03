  public:: false
  
- I remember listening to DHH(Creator of Ruby On Rails) mentioning meta-programming in a conversation. The first time he explained the con
-
  ```
     Compiling young-shell v0.1.0 (/home/ramayen/Documents/projects/Young-Shell)kljkhjjhgjghfcjkjkjhklhkjkv,koogfhgcxhjkfkljjhjgvcgjkmjhiyulijhm,bhcv
  warning: static `SLINT_EMBEDDED_RESOURCE_8` is never used
       --> /home/ramayen/Documents/projects/Young-Shell/target/debug/build/young-shell-2a829b327dc2ec24/out/app-window.rs:61344:13
        |
  61344 |      static SLINT_EMBEDDED_RESOURCE_8 : & 'static [u8] = :: core :: include_bytes ! ("/home/ramayen/Documents/projects/You...
        |             ^^^^^^^^^^^^^^^^^^^^^^^^^
        |
        = note: `#[warn(dead_code)]` (part of `#[warn(unused)]`) on by default
  
  warning: unused `Result` that must be used
    --> src/bin/ex_mac_spell.rs:32:13
     |
  32 |     let _ = spell_framework::cast_spell!(ui);
     |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     |
     = note: this `Result` may be an `Err` variant, which should be handled
     = note: `#[warn(unused_must_use)]` (part of `#[warn(unused)]`) on by default
  help: use `let _ = ...` to ignore the resulting value
     |
  32 |     let _ = let _ = spell_framework::cast_spell!(ui);
     |             +++++++
  
  warning: `young-shell` (bin "ex_mac_spell") generated 2 warnings
      Finished `dev` profile [unoptimized + debuginfo] target(s) in 11.45s
  ```
- Explain how weird errors like above happen.
- explain how recursive macro calls can happen.
- cargo expand works.
- Hoiw Lsp doesn't come for your help. Maybe also research and explain how this experience can be improved.
