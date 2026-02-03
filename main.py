import argparse
import datetime
import os
import re
import sys


def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """
    pass


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-')

def create_blog_post(title, output_dir):
    """
    Creates a new markdown blog post file with frontmatter.
    """
    date_now = datetime.datetime.now()
    date_str = date_now.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{slug}.md"
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")
        except OSError as e:
            print(f"Error creating directory {output_dir}: {e}")
            sys.exit(1)

    filepath = os.path.join(output_dir, filename)
    
    if os.path.exists(filepath):
        print(f"Error: File '{filepath}' already exists.")
        sys.exit(1)

    # MkDocs blog frontmatter template
    content = f"""---
date: {date_now.strftime("%Y-%m-%d")}
title: "{title}"
description: ""
type: post
tags:
  - 
hide:
  - navigation
authors:
  - maksudul
---

# {title}

## Introduction

Start writing your post here...

<!-- more -->

"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully created new blog post: {filepath}")
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Create a new MkDocs blog post.")
    
    parser.add_argument(
        "title", 
        help="The title of the blog post"
    )
    
    parser.add_argument(
        "-d", "--dir", 
        default="src/blog/posts",
        help="Directory where the post will be created (default: src/blog/posts)"
    )

    args = parser.parse_args()
    
    create_blog_post(args.title, args.dir)

if __name__ == "__main__":
    main()
