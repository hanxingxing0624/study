# 学习笔记系统 — 设计文档

## 概述

一个基于 Web 的个人学习笔记系统，用于记录和整理学习内容。本地运行、Markdown 编辑、文件夹+标签双组织、内置间隔重复复习。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端框架 | FastAPI |
| 模板引擎 | Jinja2 |
| 数据库 ORM | SQLAlchemy → SQLite |
| 动态交互 | Htmx |
| 客户端交互 | Alpine.js |
| Markdown 渲染 | Python-Markdown + pymdown-extensions |
| 代码高亮 | Pygments |
| 数学公式 | KaTeX / python-markdown-math |
| 知识图谱 | D3.js (CDN) |
| 复习算法 | SM-2 |

## 架构

```
浏览器 ──► FastAPI (localhost) ──► SQLite (本地文件)
                │
        ┌───────┼────────┐
        │       │        │
    Jinja2   Htmx    Alpine.js
    模板    动态交互   客户端交互
```

- 单进程应用，服务端渲染为主
- Htmx 处理无刷新提交、局部更新
- Alpine.js 处理弹窗、下拉、快捷键等纯客户端交互

## 数据模型

**Folder** — 文件夹，支持嵌套
- id, name, parent_id (可空，根文件夹)

**Note** — 笔记
- id, title, content (Markdown), folder_id (可空), status (planning/in_progress/completed)
- created_at, updated_at

**Tag** — 标签
- id, name

**NoteTag** — 笔记-标签关联
- note_id, tag_id

**NoteLink** — 笔记间双向链接
- source_id, target_id

**Review** — 复习记录（SM-2）
- note_id, reviewed_at, next_review_at, ease_factor, interval, repetitions

## 页面结构

| 路由 | 功能 |
|---|---|
| `/` | 仪表盘 — 最近笔记、统计、待复习列表 |
| `/folders` | 文件夹树形管理 |
| `/folders/{id}` | 文件夹详情 — 子文件/笔记列表 |
| `/notes/new` | 新建笔记 |
| `/notes/{id}` | 笔记查看 — 渲染后 Markdown，侧边栏含目录/反向链接 |
| `/notes/{id}/edit` | 笔记编辑 — 左侧编辑区 + 右侧预览 |
| `/tags` | 标签云 |
| `/tags/{id}` | 标签下笔记列表 |
| `/graph` | 知识图谱 — D3 力导向图 |
| `/review` | 复习面板 — 按遗忘曲线排列 |
| `/search` | 搜索 |

## 关键功能

- **Markdown 解析**：代码语法高亮 + LaTeX 数学公式 + `[[双向链接]]` 自动解析
- **知识图谱**：`/api/graph` 返回节点/边，D3.js 力导向图渲染
- **间隔重复**：SM-2 算法，评分 1-4，自动计算下次复习时间

## 项目结构

```
study/
├── main.py                 # FastAPI 入口
├── config.py               # 配置
├── models.py               # SQLAlchemy 模型
├── routes/                 # 路由模块
│   ├── notes.py
│   ├── folders.py
│   ├── tags.py
│   ├── graph.py
│   ├── review.py
│   └── search.py
├── services/               # 业务逻辑
│   ├── markdown_service.py
│   ├── review_service.py
│   └── note_service.py
├── templates/              # Jinja2 模板
│   ├── base.html
│   ├── index.html
│   ├── note_view.html
│   ├── note_edit.html
│   ├── folders.html
│   ├── tags.html
│   ├── graph.html
│   ├── review.html
│   └── search.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── data/study.db           # SQLite 文件
```

## 依赖

```
fastapi, uvicorn, jinja2, sqlalchemy
markdown, pymdown-extensions, python-markdown-math
```

前端库通过 CDN 引入：htmx, alpinejs, d3.js, katex
