---
hide:
  - navigation
  - toc
  - footer
---

# All Posts

{% for post in recent_posts(navigation.pages) %}
### [{{ post.title }}](/{{ post.url }})<br><small>{{ post.date.strftime('%B %d, %Y') }} | {% for tag in post.tags %} [{{ tag }}](tags/#{{tag}}) {% if not loop.last %} | {% endif %}{% endfor %}</small>
{{ post.description }}
<hr>
{% endfor %}
