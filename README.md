# Maksudul's Blog

Personal blog of Maksudul Haque sharing insights on programming, technology, and software engineering. Built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## 🚀 Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (for dependency management)

### Installation

Install dependencies using `uv`:

```bash
uv sync
```

### Running Locally

Start the development server to preview the site:

```bash
uv run mkdocs serve
```

The site will be available at `http://127.0.0.1:8000/`.

## ✍️ Adding a New Blog Post

This project includes a helper script `main.py` to streamline the creation of new blog posts with the correct frontmatter and file naming convention.

### Usage

Run the script providing the title of your post:

```bash
uv run main.py "Your Post Title Here"
```

This command will:
1. Generate a URL-friendly slug from the title (e.g., `your-post-title-here.md`).
2. Create a new Markdown file in `src/blog/posts/`.
3. Pre-fill the file with the necessary frontmatter (date, title, author, tags, etc.).

### Example

```bash
uv run main.py "Understanding Python Decorators"
```

**Output:**
```
Successfully created new blog post: src/blog/posts/understanding-python-decorators.md
```

You can then open the generated file and start writing your content.

## 🛠️ Deployment

This blog is hosted on GitHub Pages. Deployment is handled automatically via GitHub Actions when pushing to the `main` branch.
