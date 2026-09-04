# AGENTS.md — Collaboration & Agent Guide

Guidance for any human collaborator or AI agent working in this repository.
This is the structured classical Chinese bazi (子平命理) text library for Aether-Cycle:
every entry is a Markdown file with YAML frontmatter, and retrieval is **metadata-driven**
through the `conditions` field (array-intersection match), not fuzzy full-text search.

---

## 1. Commit discipline (MANDATORY)

Make **small, frequent, single-purpose commits**. Do not bundle unrelated work, and do not
stage hundreds/thousands of files in one commit.

- **One commit = one logical unit.** Recommended granularity for this repo:
  - A new book's `raw/*.txt` source + its parser script → one commit (`feat(scripts): ...`).
  - That book's generated `*.md` entries + its sub-`INDEX.md` → one commit
    (`feat(library): add <book> (N entries)`).
  - Baihua annotations: one JSON batch `scripts/baihua_data/baihua_<book>_<n>.json`
    **together with only the md files that batch fills** → one commit
    (`feat(baihua): fill <book> batch <n>`). Never mix different books in one baihua commit.
  - A parser/script fix or refactor → one commit (`fix(scripts):` / `refactor:`).
  - README / INDEX / docs-only edits → one commit (`docs:`).
  - `.gitignore` / tooling config → one commit (`chore:`).
- **Stage explicitly by path** (`git add <paths>`), then inspect `git status` and a scoped
  `git diff --cached --stat` before committing. Avoid `git add -A` for large mixed changes.
- Use **Conventional Commits**, English subject, imperative mood:
  `feat|fix|docs|style|refactor|test|chore(scope): subject`. Add `-m` body paragraphs for detail.
- **Push after each small unit** (or a few tightly related commits) and keep local `main`
  and `origin/main` in sync; never accumulate a single giant push.
- Every commit must leave the tree in a **valid state**: relevant parsers run and
  `scripts/validate_library.py` passes for everything committed. Prefer many green commits
  over one large risky changeset.

---

## 2. Content invariants (never violate)

- **`【原文】` is locked.** Never alter original text — variant characters, 通假字 and OCR
  forms (e.g. 夘=卯, 徳=德, 防=凶, 刼=劫) are preserved as-is. Normalize to standard
  characters **only** in retrieval fields (`day_pillar`, etc.); keep the two separate.
- **Filenames are ASCII lowercase only.** Chinese appears only inside frontmatter and body.
  File name = `<book-prefix>_<locator>`, globally unique; `id` must equal the filename stem.
- **Strict layering:** `【原文】` → (古注 / 阐微 / 命例, version-dependent) → `【白话提要】`.
  Annotations and 命例 never merge into the scripture layer.
- **Baihua only paraphrases meaning.** It must not add modern fortune judgments and must not
  fabricate content; if a passage cannot be grounded, keep the `（待补）` placeholder instead
  of inventing. (Exception: 千里命稿 is already Republican-era vernacular — no re-translation.)
- Keep retrieval metadata-driven and retain the research-only disclaimer in `README.md`.

---

## 3. Build & verify (Windows / PowerShell)

Run from the repo root. Parsers/indexers use the standard library only; validation needs PyYAML.

```powershell
$env:PYTHONIOENCODING='utf-8'          # avoid garbled Chinese console output
python -X utf8 scripts/parse_<book>.py # parse one book (clear its output dir first)
python -X utf8 scripts/build_index.py  # regenerate all INDEX.md
python -X utf8 scripts/validate_library.py   # delivery quality gate
# baihua pipeline (idempotent):
python -X utf8 scripts/export_compact.py <book_dir> [tag]   # or export_for_baihua.py
#   -> author scripts/baihua_data/baihua_<book>_<n>.json  ({id: translation})
python -X utf8 scripts/fill_baihua.py --check             # count filled / remaining
python -X utf8 scripts/fill_baihua.py                     # apply
```

- PowerShell 5.1 has **no `&&` and no `cd /d`**; chain statements with `;` and use `Set-Location`.
- Intermediate baihua exports `scripts/baihua_data/_*.txt` are generated artifacts and gitignored;
  only `baihua_*.json` translation sources are committed.

---

## 4. Environment gotchas

- **OneDrive re-wrap:** OneDrive may silently re-save a Markdown file into a loose,
  re-wrapped layout, producing an unexpectedly large diff. Before committing, inspect
  `git diff --numstat` — a normal baihua fill changes only a few lines per file. If a tracked
  file was re-wrapped, `git restore` the committed version and redo only the intended edit.
- **Push stderr false alarm:** `git push` progress goes to stderr; PowerShell may show a red
  `RemoteException` / exit code 1 even on success. Confirm the real result with
  `git status -sb` (no ahead/behind) and compare `git rev-parse HEAD` to `git rev-parse origin/main`.
- The deploy-key remote uses the configured `core.sshCommand`; do not change git identity or remote.

---

## 5. Repository layout & weights

- `core/` tier-1 (weight 8–10): qiongtongbj, zipingzhenquan, ditianchui.
- `origin-shensha/` tier-2 (weight 6): sanmingtonghui, yuanhaiziping.
- `extended/` tier-3 + supplements (weight 2–3): shenfengtongkao, yuzhaodingzhenjing,
  qianliminggao, wuxingjingji, mingliyaoyan.
- `raw/` unchanged UTF-8 sources; `scripts/` reproducible build pipeline.
- See `README.md` for the full frontmatter schema, naming table, weight order and collation notes.
