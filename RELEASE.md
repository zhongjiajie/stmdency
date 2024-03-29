# Release

Stmdency will release to [PyPI](https://pypi.org), Python Package Index, is a repository of software for the Python programming language.

## Test Release

We use [build](https://pypi.org/project/build/) to build package, and [twine](https://pypi.org/project/twine/) to
upload package to PyPi. You could first install and upgrade them by:

```bash
python3 -m pip install --upgrade pip build twine
```

It is highly recommended [releasing package to TestPyPi](#release-to-testpypi) first, to check whether the
package is correct, and then [release to PyPi](#release-to-pypi).

## Release to TestPyPi

TestPyPi is a test environment of PyPi, you could release to it to test whether the package is work or not.

1. Create an account in [TestPyPi](https://test.pypi.org/account/register/).
2. Clean unrelated files in `dist` directory, and build package `python3 setup.py clean`.
3. Build package `python3 -m build`, and you will see two new files in `dist` directory, with extension
   `.tar.gz` and `.whl`.
4. Upload to TestPyPi `python3 -m twine upload --repository testpypi dist/*`.
5. Check the package in [TestPyPi](https://test.pypi.org/project/stmdency/) and install it
   by `python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps stmdency` to
   test whether it is work or not.

## Release to PyPi

### Automatically

After you check the package in TestPyPi is correct, you can directly tag the commit and push it to GitHub, then
GitHub Actions will automatically release to PyPi based on the tag event. You can see more detail in [pypi-workflow.yml](.github/workflows/pypi.yaml).

```shell
# Preparation
VERSION=<VERSION>
git checkout -b "${VERSION}"
# For macOS
sed -i '' "s/__version__ = \".*\"/__version__ = \"${VERSION}\"/" src/stmdency/__init__.py
# For Linux
sed -i "s/__version__ = \".*\"/__version__ = \"${VERSION}\"/" src/stmdency/__init__.py
git commit -am "Release v${VERSION}"

# Tag & Auto Release in GitHub Actions
git tag -a "${VERSION}" -m "Release stmdency v${VERSION}"
git push tags/"${VERSION}"
```

## Ref

There is an official way to package project from [PyPA](https://packaging.python.org/en/latest/tutorials/packaging-projects)
