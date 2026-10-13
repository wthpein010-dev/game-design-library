---
version: alpha
name: 游戏策划知识库
description: 面向长期研习的游戏设计资料室
colors:
  primary: '#5146a4'
  ink: '#232739'
  muted: '#62677b'
  background: '#f5f6fa'
  surface: '#ffffff'
  line: '#dde0eb'
  accent: '#e7e5f7'
  success: '#23745d'
typography:
  sans:
    fontFamily: '"Microsoft YaHei", "PingFang SC", system-ui, sans-serif'
  display:
    fontFamily: '"STKaiti", "KaiTi", serif'
  mono:
    fontFamily: 'ui-monospace, monospace'
rounded:
  DEFAULT: '12px'
spacing:
  section-gap: '32px'
  page-max: '1440px'
omitted:
  - section: components
    reason: Component behavior and ownership live in UX-CONTRACT.md.
---

# 设计方向

产品型中文知识库；读者日常用电脑检索和手机阅读。参考资料室的侧边索引与书籍章节签，拒绝营销大屏和装饰性统计。签名元素是紫色侧签的学习路径，展示先修关系与实践结果。

浅灰背景、白色内容面板，紫色表达当前阅读位置。显示标题少量楷体，正文使用中文无衬线；外文标题保留原文，数字等宽。正文行高1.8，内容宽度约760px；目录与结果允许更密集。

Tokens由此文件 colors 生成 site/tokens.css（scripts/build.py），组件只使用语义变量。页面最大1440px，侧栏224px；960px以下侧栏变为顶部导航，640px以下单列。按钮至少44px高。所有滚动区统一滚动条与稳定沟槽。

共享样式：button、pill、resource-row、topic-card、detail、status。悬停用边框及背景反馈；焦点外描边；选中同时带文字和aria状态。反馈在固定live region显示，不推移页面。按需加载播放器，预留16:9区域。尊重减少动画偏好。平台原生select负责语言与排序弹出框。
