# Workflows to install

Move these into `.github/workflows/` (the token used to open this PR lacked the `workflow` scope):

```bash
mkdir -p .github/workflows && git mv ci/*.yml .github/workflows/
```

* `ci.yml` - pytest + node web tests on push/PR
* `pages.yml` - deploys `/web` to GitHub Pages on push to master (Settings -> Pages -> Source: GitHub Actions)
