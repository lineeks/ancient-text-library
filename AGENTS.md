# AGENTS.md — Collaboration & Agent Guide

Guidance for any human collaborator or AI agent working in this repository.
This is the structured classical Chinese bazi (子平命理) text library for Aether-Cycle:
every entry is a Markdown file with YAML frontmatter, and retrieval is **metadata-driven**
through the `conditions` field, not fuzzy full-text search. Matching semantics:
composite keys AND within a group (`day_master`+`month_branch`, `day_pillar`+`hour_pillar`),
independent recall dimensions OR across groups (`ten_god` / `pattern` / `shensha`);
results order by hit specificity, then tier `weight`, then path. The Python reference
(`scripts/retrieve_reference.py`) and Rust crate (`engine/`) must stay semantically identical.

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
  - A script and the artifact it generates are two commits when either is meaningful alone
    (tool first, generated output second); code + its regression test may share one commit so
    every commit stays green.
  - README / INDEX / docs-only edits → one commit (`docs:`).
  - `.gitignore` / tooling config → one commit (`chore:`).
- **Stage explicitly by path** (`git add <paths>`), then inspect `git status` and a scoped
  `git diff --cached --stat` before committing. Avoid `git add -A` for large mixed changes.
- Use **Conventional Commits**, English subject, imperative mood:
  `feat|fix|docs|style|refactor|test|chore(scope): subject`. Add `-m` body paragraphs for detail.
- **Commit on a short-lived feature branch** (see §2) and push that branch in small units;
  every pushed commit must leave the tree in a **valid state** — relevant parsers run,
  `validate_library.py` passes, and the Python/Rust tests stay green. Prefer many green
  commits over one large risky changeset.

---

## 2. Branching & pull requests via GitHub CLI (MANDATORY)

**Three-layer branch model** (full policy: `docs/branching-policy.md`):

- `main` — **release branch**: only accepts Release PRs from `develop`; every merge gets an
  annotated tag. Never commit/push directly.
- `develop` — **long-term integration branch**: all `feature/*` branches merge here. CI must
  stay green. Never commit/push directly.
- `feature/*` — **topic branch**: cut from up-to-date `develop`, one topic per branch, small
  frequent commits, push often, PR back into `develop`.
- `hotfix/*` — cut from `main`, merge into both `main` (patch tag) and `develop`.
- `release/*` — optional freeze branch from `develop`, merge into `main` (tag) and back to `develop`.

Use the **GitHub CLI (`gh`)** for remote-branch / PR / release operations.

- **Never commit directly onto `main` or `develop`.** Create a type-prefixed, ASCII-lowercase,
  hyphenated branch per topic from `develop`:
  `feature/<scope>`, `hotfix/<scope>`, `docs/<topic>`, `test/<topic>`, `chore/<topic>`
  (e.g. `feature/book-cheng-gu`, `docs/tianyi-collation`).
- **Feature PR loop (feature → develop):**

  ```powershell
  git switch develop; git pull origin develop
  git switch -c feature/<scope>      # branch from up-to-date develop
  # ... small commits per §1, push often ...
  git push -u origin HEAD             # push branch (SSH deploy-key remote already has write)
  gh pr create --base develop --head feature/<scope> --title "..." --body "..."
  gh pr checks                        # wait for checks
  gh pr merge --merge --delete-branch # preserve small-commit history; tidy the branch
  ```

- **Release PR loop (develop → main):** when a milestone is complete and `develop` CI is green:

  ```powershell
  gh pr create --base main --head develop --title "release: vX.Y.Z" --body "..."
  # final verification, then merge
  gh pr merge <n> --merge
  git switch main; git pull origin main
  git tag -a vX.Y.Z -m "Release vX.Y.Z: ..."
  git push origin vX.Y.Z
  gh release create vX.Y.Z --generate-notes   # optional
  git switch develop                           # back to long-term integration
  ```

- **Division of labor between git and gh:** plain `git push` of a branch uses the configured
  **SSH deploy-key** remote (already writable). `gh` is authenticated over **HTTPS token** and
  is used only for API operations — `gh pr create/list/view/diff/checks/merge`,
  creating the remote branch implicitly on push, `gh issue`, and `gh release create`.
  **Do NOT run `gh auth setup-git`**: it would rewrite the remote URL to HTTPS and override
  the working deploy-key `core.sshCommand`.
- **One PR = one coherent topic**; inside it, keep the small green commits from §1. Merge with
  a merge commit by default to preserve the fine-grained history the owner wants (do not squash
  a deliberate series of small commits unless asked).
- **Tags / releases:** create the annotated tag locally, push it, then optionally publish with
  `gh release create <tag> --generate-notes` (e.g. milestone `v1.0-library-1547`).
  Semantic versioning: MAJOR = five-arts coverage / schema break; MINOR = new book / new skill;
  PATCH = collation / OCR / bug fix.
- **Auth:** `gh auth status` should show account **BerryUIKI** with `repo` + `workflow` scopes.
  If `gh` is missing or unauthenticated, stop and tell the owner; do not swap remotes or invent
  credentials. Direct push to `main`/`develop` is allowed only when the owner explicitly asks for it.

---

## 3. Content invariants (never violate)

- **`【原文】` is locked.** Never alter original text — variant characters, 通假字 and OCR
  forms (e.g. 夘=卯, 徳=德, 防=凶, 刼=劫) are preserved as-is. Normalize to standard
  characters **only** in retrieval fields (`day_pillar`, etc.); keep the two separate.
  Cross-book variant readings are documented only under `docs/`, never written back into entries.
- **Filenames are ASCII lowercase only.** Chinese appears only inside frontmatter and body.
  File name = `<book-prefix>_<locator>`, globally unique; `id` must equal the filename stem.
- **Strict layering:** `【原文】` → (古注 / 阐微 / 命例, version-dependent) → `【白话提要】`.
  Annotations and 命例 never merge into the scripture layer.
- **Baihua only paraphrases meaning.** It must not add modern fortune judgments and must not
  fabricate content; if a passage cannot be grounded, keep the `（待补）` placeholder instead
  of inventing. (Exception: 千里命稿 is already Republican-era vernacular — no re-translation.)
- **Conditions enrichment is line-level and idempotent** (`scripts/enrich_conditions.py`):
  it edits only the target `conditions` lines, merges/de-dups vocabulary aligned to the
  library's existing word set, never reflows YAML and never touches the body. After any
  enrichment, regenerate `manifest.json` and rerun the tests.
- Keep retrieval metadata-driven and retain the research-only disclaimer in `README.md`.

---

## 4. Build & verify (Windows / PowerShell)

Run from the repo root. Parsers/indexers use the standard library only; validation needs PyYAML;
the Rust engine needs a Cargo toolchain.

```powershell
$env:PYTHONIOENCODING='utf-8'            # avoid garbled Chinese console output
python -X utf8 scripts/parse_<book>.py   # parse one book (clear its output dir first)
python -X utf8 scripts/build_index.py    # regenerate human-facing INDEX.md
python -X utf8 scripts/build_manifest.py # regenerate machine index manifest.json (deterministic, no timestamp)
python -X utf8 scripts/validate_library.py    # delivery quality gate (1547 entries)
python -X utf8 tests/recall_regression.py     # recall regression (Python reference matcher)
Set-Location engine; cargo test; Set-Location ..   # Rust engine unit tests (loads real manifest)
# baihua pipeline (idempotent):
python -X utf8 scripts/export_compact.py <book_dir> [tag]   # or export_for_baihua.py
#   -> author scripts/baihua_data/baihua_<book>_<n>.json  ({id: translation})
python -X utf8 scripts/fill_baihua.py --check             # count filled / remaining
python -X utf8 scripts/fill_baihua.py                     # apply
```

- `build_manifest.py` output must be byte-stable across reruns (sorted by path, no timestamp).
- When matching semantics change, update **both** `scripts/retrieve_reference.py` and
  `engine/src/lib.rs`, and add/adjust cases in `tests/recall_regression.py` and the Rust tests.
- PowerShell 5.1 has **no `&&` and no `cd /d`**; chain statements with `;` and use `Set-Location`.
- Intermediate baihua exports `scripts/baihua_data/_*.txt` are generated artifacts and gitignored;
  only `baihua_*.json` translation sources are committed.

---

## 5. Environment gotchas

- **OneDrive re-wrap:** OneDrive may silently re-save a Markdown file into a loose,
  re-wrapped layout, producing an unexpectedly large diff. Before committing, inspect
  `git diff --numstat` — a normal edit changes only a few lines per file. If a tracked
  file was re-wrapped, `git restore` the committed version and redo only the intended edit.
- **Push stderr false alarm:** `git push` progress goes to stderr; PowerShell may show a red
  `RemoteException` / non-zero exit code even on success. Confirm the real result with
  `git status -sb` (no ahead/behind) and compare `git rev-parse HEAD` to `git rev-parse origin/main`.
  A trailing `| Select-Object -First N` can also make a native command report exit code -1/101
  while the actual output is fine — judge by the printed result, and rerun without the pipe
  when the exit code matters.
- The deploy-key remote uses the configured `core.sshCommand` (private key
  `~/.ssh/id_ed25519_ancient`); do not change git identity, remote URL, or switch it to HTTPS.
- First `cargo test` fetches crates from crates.io; `engine/target/` is gitignored and
  `engine/Cargo.lock` is committed for reproducibility.

---

## 6. Repository layout & weights

- `core/` tier-1 (weight 8–10): qiongtongbj, zipingzhenquan, ditianchui.
- `origin-shensha/` tier-2 (weight 6): sanmingtonghui, yuanhaiziping.
- `extended/` tier-3 + supplements (weight 2–3): shenfengtongkao, yuzhaodingzhenjing,
  qianliminggao, wuxingjingji, mingliyaoyan.
- `raw/` unchanged UTF-8 sources; `scripts/` reproducible build pipeline; `manifest.json` the
  machine index; `engine/` the framework-agnostic Rust retrieval crate; `tests/` recall
  regression; `docs/` cross-collation notes.
- See `README.md` for the full frontmatter schema, naming table, weight order, retrieval flow
  and collation notes.
