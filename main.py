from mkdocs.utils import meta

def define_env(env):
    @env.macro
    def recent_posts(pages):
        posts = []
        for page in pages:
            with open(page.file.abs_src_path, "r") as f:
                _, metadata = meta.get_data(f.read())
                if metadata.get('type') == 'post':
                    metadata['url'] = page.file.url
                    posts.append(metadata)

        posts.sort(key=lambda x: x["date"], reverse=True)
        return posts[:6]
