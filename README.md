# sanā — privacy policy and terms

The pages Apple requires a public URL for. Served by GitHub Pages at
`https://roxelfouego.github.io/sana-legal/`, and linked from the App Store
listing, TestFlight Test Information, and the app's own Settings screen.

`source/*.md` is the only copy of the text. `_shared_context/legal/` holds
symlinks to it, the same arrangement Entelana's backend uses for its legal
pages — one file, so the published page cannot drift from the document that
was reviewed.

## Changing the text

```bash
# edit source/privacy.md or source/terms.md, then
python3 build.py
git commit -am "Update privacy policy"
git push          # Pages redeploys in about a minute
```

`build.py` is stdlib-only and renders the small markdown subset these two
documents use. That is on purpose: a legal page that cannot be rebuilt because
a virtualenv went missing is a legal page that quietly drifts from its source.

## Status

Not lawyer-reviewed. `_shared_context/legal/lyfe_legal_review_notes.md` records
what was corrected out of the first draft and why, and flags section 3 of the
terms (health and injury language) as the part most worth paying someone to read.
