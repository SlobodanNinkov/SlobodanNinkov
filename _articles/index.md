---

layout: default

title: Articles

---



<header style="text-align: left; margin: 2rem 0 4rem 0;">

&nbsp;   <h1 style="font-size: 2.5rem;">Articles</h1>

&nbsp;   <p class="tagline">Insights on System Architecture, IoT, and Technical Leadership</p>

</header>



<div class="articles-grid">

&nbsp;   {% for post in site.posts %}

&nbsp;   <article class="post-card">

&nbsp;       <div class="post-meta">{{ post.date | date: "%B %d, %Y" }}</div>

&nbsp;       <h3 class="post-title">

&nbsp;           <a href="{{ post.url | relative\_url }}">{{ post.title }}</a>

&nbsp;       </h3>

&nbsp;       <p class="post-excerpt">

&nbsp;           {{ post.excerpt | strip\_html | truncatewords: 30 }}

&nbsp;       </p>

&nbsp;       <a href="{{ post.url | relative\_url }}" class="read-more">Read Technical Brief →</a>

&nbsp;   </article>

&nbsp;   {% endfor %}

</div>

