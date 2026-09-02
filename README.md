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

> 最后更新:2026-09-03 (T5 推进 §5 #4 后续:**05 T1 财报速读基线报告设计稿 09-03 落地**,为 09-04~06 跑批 5 公司 × 5 年公告 × 4 模型提供 8 节骨架,§5 #4 大项仍按 09-02 状态 4/4 名义闭合 / 实际仍待基线报告收口) · 当前 HEAD 见 `git log -1`
> 详细计划见 [项目开发计划.md](./项目开发计划.md) §5 · 截止 **2026-09-06**(剩 3 天)

| # | 项 | 状态 | 备注 |
|---|---|---|---|
| 1 | Inspiration 资料索引 | ✅ 完成 (08-24) | [Inspiration/00-索引.md](./Inspiration/00-索引.md) · 四类共 10 条 |
| 2 | 30-50 家公司种子数据 | ✅ 完成 (08-26) | [Inspiration/公司/01-种子公司清单.md](./Inspiration/公司/01-种子公司清单.md) · 38 家 · 8 行业 · 三市覆盖 |
| 3 | pdfplumber 财报解析 demo | ✅ 完成 (08-27) | [scripts/pdfplumber_demo.py](./scripts/pdfplumber_demo.py) · 支持 `--make-sample` 与 `--extract` 双模式 · 样例输出 [samples/demo-extract.json](./samples/demo-extract.json) |
| 4 | LLM 4 类任务基线评估 | ✅ 完成 (09-02) · 05 设计稿 (09-03) | [Inspiration/LLM基线/01-4类LLM任务基线设计稿.md](./Inspiration/LLM基线/01-4类LLM任务基线设计稿.md) · **4/4 prompt 全部落地**(T1 财报速读 08-29 + T2 护城河 08-31 + T3 对标匹配 09-01 + **T4 事件归因 09-02**) · T4 两段式:规则预处理 + LLM 抽取/归因,Evidence 复用护城河 schema,`impact_dimensions` 关联 5 维 D1-D5 · **05 报告骨架**([Inspiration/LLM基线/05-T1财报速读基线报告设计稿.md](./Inspiration/LLM基线/05-T1财报速读基线报告设计稿.md))定义 8 节结构 + 5 公司 × 5 年 × 4 模型跑批契约,09-04~06 真跑后写 `05-T1财报速读基线报告-v0.1.md` 闭合 |
| 5 | 护城河评分 schema(5 维) | ✅ 完成 (08-28) | [Inspiration/护城河/01-护城河评分schema设计稿.md](./Inspiration/护城河/01-护城河评分schema设计稿.md) · 5 维等权 20 + 4 档评分 + Evidence Anchor 契约 + Pydantic schema |
| 6 | 跨行业顾问对齐(17-生物 / 20-经济 / 23-盈利) | ⏳ 未启动 | |

**整体进度**:**5 / 6(83.3%)** · §5 #4 整段闭合,仅剩 #6 跨行业对齐(需张勇拉群)

**下一步(立即可执行)**:① 09-04~06 跑 5 家头部公司(茅台/腾讯/宁德/招行/英伟达)做 4 任务 4 档盲评基线报告(T1 09-04~06 跑批骨架已落 05 设计稿,T2/T3/T4 沿用 05 结构 09-04 同步起草 06/07/08) → ② 与 17-生物 / 20-经济顾问对齐"公司画像统一字段"(需张勇拉群) → ③ Phase 0 收口(09-06)后启动 Phase 1 MVP 工程。
