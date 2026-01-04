---

layout: page

title: Ideas

permalink: /ideas/

---

Interesting ideas.

{% for note in site.ideas %}
- [{{ note.title }}]({{ note.url }}) {{ note.description }}
{% endfor %}

