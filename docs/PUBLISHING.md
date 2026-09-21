# Publish to GitHub

Use **`gawah-file/` as the Git repository root**, not its parent workspace directory. The repository includes source, seed SQL, handbook Markdown, evidence examples and the original specifications. Local databases, credentials, caches and virtual environments remain ignored.

This checkout was initialized by the Windows development sandbox. If Git reports `dubious ownership` in your terminal, use the narrowly scoped `-c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file'` option on each Git command below. This avoids changing your global Git trust settings. A regular clone that you own will not need this option.

## Before the first push

```bash
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' status --short
python scripts/check_repository.py
python -m pytest -q -p no:langsmith
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' diff --cached --stat
```

Review the staged files. The owner selected the [MIT license](../LICENSE). No remote repository or public visibility is assumed.

## First commit and push

Create an empty repository named `gawah-file` in your GitHub account. Leave GitHub's README, license and .gitignore initialization options unchecked because the local tree is already prepared. Choose public or private visibility yourself.

From this directory:

```bash
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' add .
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' commit -m "Add Gawah File investigation demo"
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' remote add origin https://github.com/YOUR_USERNAME/gawah-file.git
git -c 'safe.directory=E:/Athar Projects/Gawah Project/gawah-file' push -u origin main
```

Replace `YOUR_USERNAME` with the owner of the repository. If Git asks for author identity, configure your preferred name and email locally for this repository. Never put a token in the remote URL; use your normal Git credential manager or SSH setup.

Suggested description: **Human-reviewed digital-wallet investigations with SQL evidence, cited policy and LangGraph approval gates. Synthetic data; offline by default.**

Suggested topics: `fintech`, `langgraph`, `human-in-the-loop`, `sqlite`, `python`, `rag`, `synthetic-data`.

## After pushing

Check the Actions tab for the test matrix and open the README to confirm Mermaid and relative links render correctly. The workflow runs on Ubuntu/Python 3.11 and 3.12 and Windows/Python 3.12. Hosted CI has not run until the repository is actually pushed.

The workflow follows [GitHub's Python CI guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python). No deployment or secret configuration is needed for the offline tests.
