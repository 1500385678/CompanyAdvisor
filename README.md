# CompanyAdvisor

> 22-公司-Company 行业 Web 项目 · 内部代号 CompanyAdvisor

## 项目说明
基于张勇的 36 行业架构,CompanyAdvisor 是 公司-Company 行业的 Web 端顾问产品。

## 同步
- GitHub: https://github.com/1500385678/CompanyAdvisor
- Gitee: https://gitee.com/architectzy/CompanyAdvisor

## 自动化
- T4 每日 02:00 检查项目并更新开发计划
- T5 每日 03:00 完成小步开发并 commit + push

## Phase 0 进度速览

> 最后更新:2026-09-09 (T5 自补 跨行业 schema v0.1 草稿落地 · **§5 #6 从 0 启 → 草稿 1 落 · 共识仍 0 · 需张勇拉群** · §5 checkbox 名义 5/6(83.3%) · 实质 9/14(64.3%) · Phase 0 09-06 截止日已超期 3 天) · 当前 HEAD 见 `git log -1`
> 详细计划见 [项目开发计划.md](./项目开发计划.md) §5

| # | 项 | 状态 | 备注 |
|---|---|---|---|
| 1 | Inspiration 资料索引 | ✅ 完成 (08-24) | [Inspiration/00-索引.md](./Inspiration/00-索引.md) · 四类共 10 条 |
| 2 | 30-50 家公司种子数据 | ✅ 完成 (08-26) | [Inspiration/公司/01-种子公司清单.md](./Inspiration/公司/01-种子公司清单.md) · 38 家 · 8 行业 · 三市覆盖 |
| 3 | pdfplumber 财报解析 demo | ✅ 完成 (08-27) | [scripts/pdfplumber_demo.py](./scripts/pdfplumber_demo.py) · 支持 `--make-sample` 与 `--extract` 双模式 · 样例输出 [samples/demo-extract.json](./samples/demo-extract.json) |
| 4 | LLM 4 类任务基线评估 | ✅ 完成 (09-02) · 4/4 设计稿 (09-08 闭合) | [Inspiration/LLM基线/01-4类LLM任务基线设计稿.md](./Inspiration/LLM基线/01-4类LLM任务基线设计稿.md) · **4/4 prompt + 4/4 设计稿全部落地**(T1 财报速读 08-29 + T2 护城河 08-31 + T3 对标匹配 09-01 + T4 事件归因 09-02 + 05 设计稿 09-03 + 06 设计稿 09-05 + 07 设计稿 09-06 + **08 设计稿 09-08**) · §5 #4 实质闭合度 8/13(61.5%) · **0/4 真跑基线报告仍等 LLM provider 接入** |
| 5 | 护城河评分 schema(5 维) | ✅ 完成 (08-28) | [Inspiration/护城河/01-护城河评分schema设计稿.md](./Inspiration/护城河/01-护城河评分schema设计稿.md) · 5 维等权 20 + 4 档评分 + Evidence Anchor 契约 + Pydantic schema |
| 6 | 跨行业顾问对齐(17-生物 / 20-经济 / 23-盈利) | 🟡 草稿 1 落 (09-09) · 共识 0 | [Inspiration/跨行业/01-跨行业公司画像字段schema设计稿.md](./Inspiration/跨行业/01-跨行业公司画像字段schema设计稿.md) · **7 大类 23 通用字段 + 3 行业扩展位 + 5 一致性约束 + 3 批对齐建议** · 22-公司 cron 03:30 自补(沿用 08-29 T5 自补模式) · §5 #6 实际仍 `[ ]` 未对齐 · **需张勇拉群才能升 v0.2** |

**整体进度**:**5 / 6(83.3%)** · §5 #4 名义 4/4 prompt + 4/4 设计稿已闭合(0/4 真跑基线报告待启) · §5 #6 13 日挂零 → 09-09 启(草稿 1 落,共识 0)

**下一步(立即可执行)**:① 4 设计稿就位后等 LLM provider 接入 → 跑 5 公司 × 5 年公告 × 4 模型基线报告 4 份 → ② 与 17-生物 / 20-经济 / 23-盈利 顾问对齐"公司画像统一字段"v0.2(沿用 09-09 草稿 schema;需张勇拉群) → ③ Phase 0 收口后启动 Phase 1 MVP 工程。
