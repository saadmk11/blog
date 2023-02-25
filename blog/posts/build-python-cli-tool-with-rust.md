---
title: Build a Python CLI Tool with Rust
description: A simple example of how to build a Python CLI tool with Rust
date: 2023-02-25
type: post
tags:
    - rust
    - python
    - cli
    - tutorial
hide:
  - navigation
---

# Build a Python CLI Tool with Rust <br><small>{{ page.meta.date.strftime('%B %d, %Y') }}</small>

## Introduction

In this tutorial, we will build a simple Python CLI tool with Rust.
The tool will search for a given string in the given directory and print the file names that contain the string.

## Prerequisites

To follow this tutorial, you need to have the following installed:

- Rust
- Cargo
- Python 3.7 or later

## Create a New Rust project

First, we need to create a new Rust project that will contain the code for our CLI tool.
We will use the `cargo` to create the project and we will call it `findrs`:

```bash
cargo new --bin findrs
```

The directory structure of the project will look like this:

```bash
findrs/
├── Cargo.toml
└── src
    └── main.rs
```

### Parse Command-Line Arguments

#### Add the `clap` Crate to the Project

The `clap` crate is a command-line argument parser for Rust. We can use this crate to parse the command-line arguments for `findrs`.
To add the `clap` to our project, we can run the following command:

```bash
cargo add clap --features derive # (1)!
```

1.  This will add the latest version of `clap` crate to the `Cargo.toml` file under the `[dependencies]` section.
    ```yaml
    [dependencies]
    clap = { version = "4.1.1", features = ["derive"] }
    ```

#### Add `clap` Argument Parser to the Project

Now, we can add the `clap` argument parser our the project. Let's add the following code to the `main.rs` file:

```rust
use std::path::PathBuf;

use clap::Parser;  // (1)!

#[derive(Debug, Parser)]  // (2)!
#[command(about = "Find all files containing a given name.")]  // (3)!
pub struct Arguments {
    /// Name to find.  // (4)!
    #[arg(short, long)]  // (5)!
    pub name: String, // (6)!
    /// Path to to check.
    #[arg(default_value = ".")] // (7)!
    pub path: PathBuf, // (8)!
}

fn main() {
    let args = Arguments::parse();  // (9)!
    println!("{:?}", args);
}
```

1.  Import `calp`'s `Parser` trait.
2.  Derive the `Debug` and `Parser` traits for the `Arguments` struct.
3.  Add the `about` attributes to the `Arguments` struct. This will show-up in the help message.
4.  Add help message to the `name` field.
5.  Add the `arg` attributes to the `name` field. This will add the `--name` and `-n` flags to the `findrs` CLI tool.
7.  Add the `name` field to the `Arguments` struct. This field will be used to store the name that we want to match with the file names.
8.  Add the `default_value` attribute to the `path` field. This will set the default value of the `path` field to `.` (current directory).
9.  Add the `path` field to the `Arguments` struct. This field will be used to store the path to the directory that we want to search for the given name.
10.  Parse the command-line arguments and store them in the `args` variable.

Now, we can run the `findrs` CLI tool with the `--help` flag to see the help message:

```bash
cargo run -- --help
```

Output:
```bash
Find all files containing a given name.

Usage: findrs --name <NAME> [PATH]

Arguments:
  [PATH]  Path to to check [default: .]

Options:
  -n, --name <NAME>  Name to find
  -h, --help         Print help
```

You can run the `findrs` CLI tool with cargo by running the following command:

```bash
cargo run -- --name test ~/Desktop
```

Output:
```bash
Arguments { name: "test", path: "/home/saad/Desktop" }
```

Here you can see that the `name` and `path` fields of the `Arguments` struct are set to the values that we passed to the `findrs` CLI tool.

### Search for the Files that Contain the Given Name

#### Add the `walkdir` Crate to the Project

The `walkdir` crate is a Rust library for walking a directory tree. We can use this crate to search for the files that contain the given name.
To add the `walkdir` to our project, we can run the following command:


```bash
cargo add workdir # (1)!
```

1.  This will add the latest version of `workdir` crate to the `Cargo.toml` file under the `[dependencies]` section.
    ```yaml hl_lines="3"
    [dependencies]
    clap = { version = "4.1.6", features = ["derive"] }
    walkdir = "2.3.2"
    ```

#### Update the `main.rs` File

Now, we can update the `main.rs` file to search for the files that contain the given name. Let's add the following code to the `main.rs` file:

```rust hl_lines="1 5 21-29"
use std::ffi::OsStr;  // (1)!
use std::path::PathBuf;

use clap::Parser;
use walkdir::WalkDir;  // (2)!

#[derive(Debug, Parser)]
#[command(author, about = "Find all files containing a given name.")]
pub struct Arguments {
    /// Name to find.
    #[arg(short, long)]
    pub name: String,
    /// Path to to check.
    #[arg(default_value = ".")]
    pub path: PathBuf,
}

fn main() {
    let args = Arguments::parse();

    for entry in WalkDir::new(&args.path).into_iter().filter_map(|e| e.ok()) {  // (3)!
        let path = entry.path();
        if path.is_file() {  // (4)!
            match &path.file_name().and_then(OsStr::to_str) {  // (5)!
                Some(name) if name.contains(&args.name) => println!("{}", path.display()),  // (6)!
                _ => (),  // (7)!
            }
        }
    }
}
```

1.  Import `OsStr` struct.
2. Import `walkdir`'s `WalkDir` struct.
3. Iterate over all entries in the given directory and ignore any errors that may arise.
4. Check if the entry is a file.
5. Get the file name of the entry and convert it to a `&str`.
6. If the file name contains the given name, print the path to the file.
7. If the file name doesn't contain the given name or is `None` variant, do nothing.

Now, we can run the `findrs` CLI tool with the `--name` flag and the directory to search for the files that contain the given name:

```bash
cargo run -- --name test ~/Desktop
```

Output:
```bash
/home/saad/Desktop/test.txt
/home/saad/Desktop/testing.py
```

## Prepare the Project to Run with Python

### Install `maturin`

Install `maturin` inside a `virtualenv` by running the following command:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip maturin
```

### Add `pyproject.toml` File

Now, we can add the `pyproject.toml` file at the root of the project. 

```bash
findrs/
├── Cargo.toml
├── pyproject.toml
└── src
    └── main.rs
```

Let's add the following code to the `pyproject.toml` file:

```toml
[build-system]
requires = ["maturin>=0.14,<0.15"] # (1)!
build-backend = "maturin" # (2)!

[project]
name = "findrs" # (3)!
description = "Find all files containing a given name." # (4)!
requires-python = ">=3.7" # (5)!

[tool.maturin]
bindings = "bin" # (6)!
strip = true # (7)!
```

1.  This specifies the version of `maturin` that we want to use.
2.  We need to use `maturin` as the build backend for the project.
3.  Specify the name of the package as `findrs`.
4.  Add the description of the package.
5.  Specify the minimum version of Python that we want to support.
6.  In our case, we want to generate bindings for a binary because it is a CLI tool.
7.  Strip the library for minimum file size.

### Build and install the module with `maturin`

#### For Development

For local development, the maturin can be used to build the package and install it to virtualenv.

```bash
maturin develop
```

We can also run pip install directly from project root directory:

```bash
pip install -e .
```

Now we can run the `findrs` CLI tool directly from the terminal:

```bash
findrs --name test ~/Desktop
```

#### Create a wheel for distribution

Now, we can create wheels for distribution:

```bash
maturin build
```

This will create a `wheel` file in the `target/wheels` directory.

We can install the wheel file using `pip`:

```bash
pip install target/wheels/<file-name>.whl
```

### Publish the Package to PyPI

Now, we can publish the package to PyPI. First, we need to create an account on [PyPI](https://pypi.org/).
Then run the following command to upload the package to PyPI:

```bash
maturin publish
```

## Integrate GitHub Actions

We can use GitHub actions to run the tests and publish the package to PyPI automatically.
To generate the GitHub actions workflow file, we can run the following command:

```bash
maturin generate-ci github
```

## Useful References

**Install Rust:** [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install)

**Rust Book:** [https://doc.rust-lang.org/book/](https://doc.rust-lang.org/book/)

**Maturin Documentation:** [https://www.maturin.rs/index.html](https://www.maturin.rs/index.html)


## Conclusion

`maturin` has made it very easy to build and publish Python packages built with Rust.
This tutorial showcases a simple example of that. I hope you found this useful.
