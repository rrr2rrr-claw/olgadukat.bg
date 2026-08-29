# olgadukat.bg

Public production repository for the static website at https://olgadukat.bg.

## Editing content

Pages CMS reads `.pages.yml` from this repository.

- Structured editable data lives in `data/*.yml`.
- Images are uploaded to `images/`.
- Current live pages are static HTML files in the repository root.
- Main page text is editable in `Homepage content` and `Pricing`.
- Books, consultations, and birth pages are editable in `Books page`, `Consultations page`, and `Birth page`.
- GitHub Actions regenerates the HTML pages after structured data files change.
- `HTML pages` remains available for advanced manual fixes.

Do not commit secrets, private notes, credentials, or unpublished sensitive material here.
