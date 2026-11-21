# Releasing

## Python package → PyPI

Automated via `.github/workflows/publish.yml` on a GitHub Release, using **PyPI
Trusted Publishing** (no token stored).

One-time setup: on PyPI, create the `kavach` project and add a *trusted
publisher* for this repo (`hxshxnsivx-hub/S.H.I.E.L.D-101`, workflow
`publish.yml`). Then:

```bash
# bump version in pyproject.toml, commit, then tag + release
git tag v0.0.1 && git push origin v0.0.1
# create a GitHub Release for the tag -> the workflow builds & publishes
```

Build locally to check:

```bash
pip install build
python -m build            # produces dist/*.whl and *.tar.gz
```

## JS client → npm

```bash
cd clients/js
npm publish --access public      # needs: npm login  (or NPM_TOKEN in CI)
```

## Container image

```bash
docker build -t <registry>/kavach:<tag> .
docker push <registry>/kavach:<tag>
```
