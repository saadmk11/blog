from mkdocs.utils import meta

def define_env(env):
    @env.macro
    def recent_posts(pages, limit=None):
        posts = []
        for page in pages:
            with open(page.file.abs_src_path, "r") as f:
                _, metadata = meta.get_data(f.read())
                if metadata.get('type') == 'post':
                    metadata['url'] = page.file.url
                    posts.append(metadata)

        posts.sort(key=lambda x: x["date"], reverse=True)

        if limit:
            posts = posts[:limit]
        return posts
