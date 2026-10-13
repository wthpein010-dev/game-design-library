# 交互约定

- 搜索、分类、类型、语言、排序、页码保存URL；刷新和浏览器前进后退恢复状态。中文输入法组合期间不刷新结果，清除立即生效。
- 资源、课程、专题、更新记录共用导航和视觉词汇。资源每页24条；明确下一页和上一页。无结果可重置筛选。加载失败保留框架并允许重试。
- 资源详情用页面区域，返回列表保留筛选。外部内容渲染为纯文本；课程HTML构建期白名单清洗。视频只在点击播放时创建原站iframe，保留分集p参数。
- 收藏、状态、笔记存本机浏览器。保存失败明确提示；导入采用严格结构校验与合并，已有同ID记录优先保留，避免覆盖新笔记。导出为私有备份，不上传GitHub。
- 答题反馈只说明本题演算，不标记整课掌握。来源检查成功不等于人工审读。

| Capability | Canonical owner | Source of truth | Variants | Verification |
|---|---|---|---|---|
| Select/Listbox | site/index.html native select | UX-CONTRACT.md | 语言、排序 | 浏览器键盘与弹出 |
| Form | site/app.mjs | UX-CONTRACT.md | 笔记、导入 | 状态测试 |
| Scrollbar | site/styles.css | DESIGN.md | 文档、代码 | 手机与桌面检查 |
| Toast | site/app.mjs notify | UX-CONTRACT.md | 保存、错误 | aria-live |
| CRUD | site/core.mjs | UX-CONTRACT.md | 本地学习记录 | 备份合并测试 |

语言zh-CN；日期明确原文发表和本库收录。没有账号权限、付费、远端个人记录或删除操作。所有按钮可键盘访问，动作与导航分别使用button与a。
