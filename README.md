# olgadukat.bg

Public production repository for the static website at https://olgadukat.bg.

## Editing content

Pages CMS reads `.pages.yml` from this repository.

- Structured editable data lives in `data/*.yml`.
- Images are uploaded to `images/`.
- Current live pages are static HTML files in the repository root.
- Homepage text is editable in `Homepage content` and `Pricing`; GitHub Actions regenerates `index.html` after those files change.
- Other pages can still be edited in the `HTML pages` section until they are migrated to structured fields too.

Do not commit secrets, private notes, credentials, or unpublished sensitive material here.
