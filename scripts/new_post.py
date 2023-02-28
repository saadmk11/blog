import argparse
import datetime
import re
from dataclasses import asdict, dataclass, field

import yaml

TEMPLATE = """\
---
{metadata}
---

# {title} <br><small>{post_fmt_date}</small>

## Introduction


## References


## Conclusion
"""


@dataclass
class Post:
    title: str
    description: str
    date: datetime.date | None = None
    tags: list[str] = field(default_factory=list)
    type: str = "post"
    hide: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.date = self.date or datetime.date.today()
        self.hide = self.hide or ["navigation"]

    def to_yaml(self):
        return yaml.dump(asdict(self))


def slugify(text):
    return re.sub(r"\W+", "-", text.lower()).strip("-")


def main() -> int:
    """
    Create a new blog post.

    Example:
        python ./scripts/new_post.py  "Title" "Description" --tags python django --date 2021-01-01
    :return:
    """
    parser = argparse.ArgumentParser("Create a new blog post.")
    parser.add_argument("title", help="The title of the post")
    parser.add_argument("description", help="The description of the post")
    parser.add_argument("--tags", help="The tags of the post", nargs="+")
    parser.add_argument(
        "--date", help="The date of the post", type=datetime.date.fromisoformat
    )
    args = parser.parse_args()

    post = Post(
        title=args.title, description=args.description, tags=args.tags, date=args.date
    )

    with open(f"blog/posts/{slugify(post.title)}.md", "w") as f:
        f.write(
            TEMPLATE.format(
                title=post.title,
                post_fmt_date=post.date.strftime("%B %d, %Y"),
                metadata=post.to_yaml(),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
