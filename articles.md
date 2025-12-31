---
layout: page
title: Articles
permalink: /articles/
---

<header style="text-align: left; margin: 2rem 0 4rem 0;">
    <h1 style="font-size: 2.5rem;">Articles</h1>
    <p class="tagline">Insights on System Architecture, IoT, and Technical Leadership</p>
</header>

<div class="articles-grid">
    {% for post in site.posts %}
    <article class="post-card">
        <div class="post-meta">{{ post.date | date: "%B %d, %Y" }}</div>
        <h3 class="post-title">
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </h3>
        <p class="post-excerpt">
            {{ post.excerpt | strip_html | truncatewords: 30 }}
        </p>
        <a href="{{ post.url | relative_url }}" class="read-more">Read Technical Brief →</a>
    </article>
    {% endfor %}
</div>

