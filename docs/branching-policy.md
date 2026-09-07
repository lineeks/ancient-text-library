# 分支管理规范（Branching Policy）

> 本仓库采用 **三层分支模型**：`main`（发布）+ `develop`（长期集成）+ `feature/*`（功能）。
> 所有开发在 `feature/*` 上进行，小步 commit、频繁 Push，通过 PR 合并入 `develop`；
> 阶段性完成后从 `develop` 提 Release PR 合并入 `main` 并打 tag。

---

## 1. 分支模型总览

```
main ──────────────●──────────────────●────────  （发布分支，仅接受 Release PR + tag）
                    ↑ merge              ↑ merge
develop ──●──●──●──┘──●──●──●──────────┘──────  （长期集成分支，所有 feature 合并目标）
           ↑     ↑        ↑
     feature/a  feature/b  feature/c               （功能分支，从 develop 切，合并回 develop）
```

| 分支 | 角色 | 来源 | 合并目标 | 可否直接 push |
|---|---|---|---|---|
| `main` | 发布分支：阶段性完成的稳定版本，打 tag | — | 仅接受 `develop` 的 Release PR | **禁止**，必须走 PR |
| `develop` | 长期集成分支：所有功能的集成与验证 | `main` | `feature/*` 合入；阶段性合入 `main` | **禁止**，必须走 PR |
| `feature/*` | 功能分支：单一主题的开发工作 | `develop` | `develop` | 可以（小步频繁 push） |
| `hotfix/*` | 紧急修复：生产问题的快速修复 | `main` | `main` + `develop` | 可以 |
| `release/*` | 发布准备：版本冻结、文档收尾（可选） | `develop` | `main` + `develop` | 可以 |

---

## 2. 各分支职责

### 2.1 `main` — 发布分支
- 只存放**阶段性完成、验证通过**的稳定版本
- 每次合并入 `main` 必须打 **annotated tag**（语义化版本）
- 不直接 commit，不直接 push，**仅通过 Release PR 合并**
- `main` 的每个 commit 对应一个可发布的版本

### 2.2 `develop` — 长期集成分支
- 所有 `feature/*` 分支的**唯一合并目标**
- 持续集成最新功能，CI 必须保持全绿
- 不直接 commit，不直接 push，**仅通过 feature PR 合并**
- 阶段性功能全部完成、验证通过后，提 Release PR 合并入 `main`

### 2.3 `feature/*` — 功能分支
- **单一主题**：一个 feature 分支只做一件事（一部书入库 / 一个工程化改进 / 一篇校勘）
- 从最新 `develop` 切出，命名全小写、用连字符
- 小步频繁 commit（每个 commit 单一目的、可独立验证）
- 频繁 push（每天至少 push 一次，避免本地丢失）
- 完成后提 PR 合并入 `develop`，CI 绿后 merge，**合并后删除分支**

### 2.4 `hotfix/*` — 紧急修复分支
- 从 `main` 切出，用于修复生产/发布版本的紧急问题
- 修复后同时合并入 `main`（打 patch tag）和 `develop`
- 命名：`hotfix/简短描述`

### 2.5 `release/*` — 发布准备分支（可选）
- 从 `develop` 切出，用于版本冻结、文档收尾、最终验证
- 完成后合并入 `main`（打 tag）并回合并入 `develop`
- 命名：`release/vX.Y.0`
- 小项目可省略此分支，直接从 `develop` 提 Release PR 到 `main`

---

## 3. 分支命名规范

| 类型 | 命名格式 | 示例 |
|---|---|---|
| 功能 | `feature/<主题>` | `feature/book-cheng-gu`、`feature/ci-workflow`、`feature/collation-yima` |
| 紧急修复 | `hotfix/<问题>` | `hotfix/manifest-total` |
| 发布 | `release/v<版本>` | `release/v1.2.0` |
| 文档 | `docs/<主题>` | `docs/five-arts-roadmap`、`docs/branching-policy` |

- 全小写英文，用连字符 `-` 分隔，禁止中文、空格、下划线
- 主题简短明确，能一眼看出分支做什么
- 一个分支一个主题，不做大杂烩

---

## 4. Commit 规范

### 4.1 Conventional Commits
所有 commit message 遵循 Conventional Commits 格式：

```
<type>(<scope>): <subject>

<body>
```

| type | 用途 | 示例 |
|---|---|---|
| `feat` | 新增功能/新书/新条目 | `feat(book): add 李虚中命书 30 entries` |
| `fix` | 修复 bug | `fix(parser): correct 20th-day weight to 1.5 liang` |
| `docs` | 文档变更 | `docs(readme): update five-arts category table` |
| `style` | 格式（不影响逻辑） | `style(frontmatter): normalize indentation` |
| `refactor` | 重构（不改变行为） | `refactor(retrieval): extract match groups` |
| `test` | 测试相关 | `test(golden): add 6 new chart fixtures` |
| `chore` | 构建/工具/依赖 | `chore(ci): add validate step` |
| `perf` | 性能优化 | `perf(engine): optimize entry scan` |

### 4.2 小步 Commit 原则
- **一个 commit 一个目的**：不要把"新增书 + 改检索器 + 更新文档"混在一个 commit
- **每个 commit 可独立验证**：commit 后测试应能通过（或至少不破坏已有功能）
- **显式按路径 git add**：`git add path/to/file`，**禁止 `git add -A`** 大杂烩
- **commit message 用英文祈使句**，body 可补充细节（中文/英文均可）
- **频繁 commit**：每完成一个可验证的小单元就 commit，不要攒一大堆

---

## 5. PR 与合并流程

### 5.1 Feature PR（feature → develop）
```bash
# 1. 从最新 develop 切功能分支
git switch develop
git pull origin develop
git switch -c feature/my-topic

# 2. 小步开发、频繁 commit、频繁 push
git add path/to/file
git commit -m "feat(...): ..."
git push origin feature/my-topic

# 3. 完成后提 PR（base = develop）
gh pr create --base develop --title "feat: ..." --body "..."

# 4. CI 全绿后合并（保留 merge commit，删分支）
gh pr merge <number> --merge --delete-branch
```

### 5.2 Release PR（develop → main）
```bash
# 1. 阶段性完成后，从 develop 提 PR 到 main
gh pr create --base main --head develop --title "release: vX.Y.Z" --body "..."

# 2. CI 全绿、最终验证后合并
gh pr merge <number> --merge

# 3. 切到 main，打 annotated tag，推送
git switch main
git pull origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z: ..."
git push origin vX.Y.Z

# 4. 切回 develop 继续
git switch develop
```

### 5.3 Hotfix PR（hotfix → main + develop）
```bash
git switch main
git pull origin main
git switch -c hotfix/fix-xxx
# ... 修复、commit、push ...
gh pr create --base main --title "hotfix: ..."
gh pr merge <n> --merge --delete-branch
git switch main && git pull
git tag -a vX.Y.Z+1 -m "hotfix ..." && git push origin vX.Y.Z+1
# 同步到 develop
git switch develop && git pull
git merge main
git push origin develop
```

---

## 6. Push 与远程协作

### 6.1 走 GitHub CLI（gh）
- **PR 创建/合并/查看**：统一用 `gh` CLI
- **分支 push**：用 `git push origin <branch>`（SSH deploy key）
- **禁止 `gh auth setup-git`**：会把 remote 改成 HTTPS，覆盖可用的 deploy key
- `gh` 只做 PR/分支/release API，不替代 git push

### 6.2 频繁 Push
- feature 分支**每天至少 push 一次**，避免本地工作丢失
- 小步 push：每完成 1-3 个 commit 就 push 一次
- push 不要求功能完成，中间状态也可以 push（但 commit 应可独立验证）
- PR 可以在功能完成前创建（Draft PR），便于提前评审

### 6.3 合并策略
- **默认 `--merge`**（保留 merge commit，保留小步历史）
- 不用 `--squash`（会丢失小步 commit 历史）
- 不用 `--rebase`（会重写历史，冲突风险高）
- 合并后**自动删除分支**（`--delete-branch`）

---

## 7. 版本化与 Tag

### 7.1 语义化版本
| 版本位 | 触发条件 | 示例 |
|---|---|---|
| MAJOR (X.0.0) | 五术全覆盖 / 顶层目录大重构 / schema 不兼容升级 | v2.0.0 |
| MINOR (x.Y.0) | 新增一部书 / 新增一个术类 / 检索语义升级 | v1.2.0 |
| PATCH (x.y.Z) | 校勘 / OCR 校正 / 白话修正 / bug 修复 | v1.1.1 |

### 7.2 Tag 规则
- 每次合并入 `main` 必须打 **annotated tag**（`git tag -a`）
- tag 信息包含：版本号、新增书目、条目数、校勘文档、breaking changes
- tag 推送：`git push origin vX.Y.Z`
- 可选：`gh release create vX.Y.Z --generate-notes` 生成 GitHub Release

---

## 8. CI 与质量门

所有 PR 必须通过 CI 才能合并：
1. `validate_library.py`：Frontmatter 规范、id 唯一、枚举合法、正文分层
2. `tests/recall_regression.py`：Python 召回回归 + golden 对拍 + 自召回
3. `cargo test`：Rust engine 单测 + golden 对拍 + 自召回 + 正文加载
4. manifest 确定性检查：`build_manifest.py` 重跑无 diff

CI 配置见 `.github/workflows/ci.yml`。

---

## 9. 常见场景示例

### 场景 A：新增一部书
1. `git switch develop && git pull && git switch -c feature/book-li-xu-zhong`
2. 写 parser、生成 md、build_manifest、validate、测试
3. 小步 commit：`feat(parser): ...` → `feat(book): add 30 entries` → `test: ...` → `docs: ...`
4. 频繁 push
5. `gh pr create --base develop`，CI 绿后 `gh pr merge --merge --delete-branch`

### 场景 B：工程化改进（如 CI 配置）
1. `git switch develop && git pull && git switch -c feature/ci-workflow`
2. 写 `.github/workflows/ci.yml`，本地验证
3. commit + push + PR → develop

### 场景 C：阶段性发布（命部完成）
1. 确认 develop CI 全绿、所有 feature 已合并
2. `gh pr create --base main --head develop --title "release: v1.2.0 - 命部补全完成"`
3. 最终验证后 merge
4. `git switch main && git pull && git tag -a v1.2.0 -m "..." && git push origin v1.2.0`
5. `gh release create v1.2.0 --generate-notes`
6. `git switch develop` 继续

---

## 10. 铁律总结

1. **main 只发布，develop 只集成，feature 只做一件事**
2. **文档先行**：分支/流程/规范变更先写文档，再执行
3. **小步 commit，频繁 push**：每个 commit 单一目的、可独立验证
4. **显式 git add，禁止 git add -A**
5. **所有合并走 PR + CI，禁止直接 push main/develop**
6. **走 gh CLI 做 PR，禁止 gh auth setup-git**
7. **默认 merge commit，保留小步历史，合并后删分支**
8. **每次入 main 必打 annotated tag**

---

*本规范 v1.0 于 2026-09 制定，随项目演进持续更新。*
