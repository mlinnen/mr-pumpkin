# Decision: Jekyll for GitHub Pages Site (Issue #57)

**By:** Vi (Backend Dev)  
**Date:** 2026-03-03  
**Issue:** #57

---

## Technology Choice: Jekyll 4.3

**Decision:** Use Jekyll (not Hugo, MkDocs, or plain HTML) for the GitHub Pages site.

**Rationale:**
- Jekyll is GitHub's native Pages engine — no custom CI build is strictly required; GitHub can render Jekyll automatically if needed
- Native pagination support via `jekyll-paginate`
- Liquid templating allows DRY layouts (`_layouts/`, `_data/navigation.yml`)
- Zero JavaScript framework overhead — pure server-rendered HTML
- SEO tag support via `jekyll-seo-tag`

---

## Structure Decisions

**Custom layout over minima theme:**  
Used a fully custom `_layouts/default.html` instead of the `minima` theme to get full design control for the dark pumpkin aesthetic. Minima is light-themed and would require deep overrides.

**Blog posts in `_posts/`:**  
Moved blog content to `docs/_posts/YYYY-MM-DD-title.md` (Jekyll convention) rather than keeping in `docs/blog/`. The `docs/blog/` folder is preserved with the original file untouched.

**Navigation via `_data/navigation.yml`:**  
All nav items defined once in a YAML data file and iterated in the layout — single source of truth.

**Search: GitHub redirect, not lunr.js:**  
Used a simple GitHub search redirect rather than lunr.js to avoid a build-time index step and heavy JS. lunr.js can be added later when post count grows.

---

## Front Matter Convention

All existing `docs/*.md` files received Jekyll front matter prepended (non-destructive — original content unchanged):
- `layout: page`
- `title:` (matching the existing `# H1`)
- `permalink:` (matching existing relative links in the docs)
- `description:` (short summary for SEO)

---

## CI/CD: squad-docs.yml

Updated workflow to:
1. Use `ruby/setup-ruby@v1` with Ruby 3.2 and bundler caching
2. Run `bundle exec jekyll build` from the `docs/` directory
3. Output to `_site/` at repo root
4. Upload via `actions/upload-pages-artifact@v3`
5. Deploy via `actions/deploy-pages@v4` in a separate `deploy` job

Trigger: push to `preview` branch touching `docs/**` or the workflow file.
