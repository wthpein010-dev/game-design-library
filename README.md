# 游戏策划知识库

一个持续积累的游戏设计资料室：原理、案例、视频、课程与个人学习记录。

**网站：https://wthpein010-dev.github.io/game-design-library/**

## 内容

- 50课正文、知识结构、200道练习及原站音频。
- 63个B站视频／分集，按需加载原站播放器。
- 12个专题：玩法、心理、概率、奖励、决策、经济、交易、验证、关卡、叙事、制作与案例拆解。
- 公开文章索引与来源状态，每天补录新旧资料。自动索引不等于人工审读。
- 收藏、阅读状态、笔记与备份导入导出。个人记录仅存当前浏览器，不自动跨设备同步。

## 免费部署与数据库

独立公开GitHub仓库 + GitHub Pages + GitHub Actions，无付费数据库或API依赖。数据库为构建生成的SQLite快照，可下载并用DB Browser for SQLite等工具打开。网站查询同一快照的JSON，支持中文关键词、类型、主题、语言和排序。

[下载数据库](https://wthpein010-dev.github.io/game-design-library/data/knowledge.sqlite) · [JSON索引](https://wthpein010-dev.github.io/game-design-library/data/catalog.json)

表：`resources`（资料）、`sources`（来源）、`lessons`（课程）、`sections`（正文）、`sync_runs`（同步记录）、`revisions`（收录与修订事件）。JSON源数据在 `data/`，SQLite与浏览器数据在 `site/data/`。

```sql
SELECT title, author, url FROM resources WHERE category='数值与概率';
SELECT source_id, COUNT(*) FROM resources GROUP BY source_id;
```

## 每日维护

Actions计划每天北京时间08:20运行，平台可能延迟；公开仓库长期无活动也可能暂停schedule，应定期查看运行状态。手动可在Actions页面运行 `Update and publish library`。不需要开着本机。

每次读取允许来源的RSS，按站点地图每源最多补录8个历史条目。元数据URL去重，保留发表、收录、检查和变更时间；HTTP/HTTPS在已验证站点统一，B站分集保留。每源限速，尊重robots及访问限制。部分失败保留成功结果；全部失败保留旧数据、发布失败状态并使任务失败。来源与更新页显示错误和剩余历史条数。

目前自动来源：Designer Notes、Game Design Concepts、GDKeys。Lostgarden和indienova暂作参考入口，不绕过其限制。题材过滤规则在来源配置中，避免收录明显无关的个人动态和报名通知。分类由标题关键词初分，作者论点未由自动程序验证。

新增来源：在 `data/sources.json` 登记站点、RSS、站点地图、语言、允许历史路径和排除规则，先实际验证公开权限、robots与内容相关性，再启用。新资源优先保留标题、作者、日期、简短摘要和原始链接，不镜像第三方全文或视频。资料提交通道为GitHub Issues。

## 本地开发

Python 3.12+、Node 22+。

```text
python scripts/build.py
python -m http.server 8767 --directory site
```

打开 http://localhost:8767 。同步：`python scripts/sync.py --limit 8`。完整回归只在Ubuntu CI运行；Windows不运行全仓回归或ClickFlow。定向校验：`python -m unittest tests.test_sync`、`node --test tests/core.test.mjs`。

## 来源与边界

用户指定参考：[麦克老狼档案馆](https://docs.qq.com/sheet/DVkhwV25kSGNWeGpl?tab=mcqid4)、[独立游戏共建知识百科](https://docs.qq.com/sheet/DWWtxbVFWZ25OZWJU?tab=BB08J2)。实际核验导航与可见样例，借鉴字段、分类与案例思路，未宣称全量导入这两份表格。原50课来自已公开的[游戏设计研习册](https://wthpein010-dev.github.io/ai-application-hub/projects/game-design-textbook/)。

外部文章、书籍、音视频版权归原作者；本站提供索引和短摘要，无权授予第三方内容再分发许可。站内学习材料的公开不代表用户已掌握，收藏和已读仅为个人记录。外部音频、视频的可用性依赖原站。
