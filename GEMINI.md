# Gemini Transformation Plan

The goal of this transformation is to update the existing Jekyll website to have the look and feel of `example.html`. This involves changing the site from a multi-page blog to a single-page portfolio with a modern, minimalist design.

## Plan

1.  **Create a New Layout:**
    *   Create a new layout file: `_layouts/portfolio.html`.
    *   This file will be based on the structure of `example.html`.

2.  **Create a New CSS File:**
    *   Create a new CSS file: `assets/css/portfolio.css`.
    *   Extract the CSS from the `<style>` block in `example.html` and place it in this new file.

3.  **Update the New Layout:**
    *   Modify `_layouts/portfolio.html` to link to the new `assets/css/portfolio.css` stylesheet instead of having the CSS embedded.

4.  **Update the Homepage (`index.md`):**
    *   Change the `layout` in the front matter of `index.md` to `portfolio`.
    *   Restructure the content of `index.md` to match the sections in `example.html`:
        *   Hero Section
        *   "What I Build" Section
        *   "How I Work" Section
        *   "Experience" Section
        *   Footer
    *   The existing content from `index.md` will be mapped to these new sections.

5.  **Update Configuration (`_config.yml`):**
    *   Remove the `navbar-links` configuration, as the new design is a single-page site and does not have a navigation bar.

6.  **Review and Cleanup:**
    *   After the initial changes, a review will be conducted to identify any further adjustments or file cleanup needed to fully align the site with the new design. No files will be removed in this initial phase.
