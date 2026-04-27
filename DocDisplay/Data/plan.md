# DocDisplay 子專案規劃

## 目的

展示簡易文章的靜態文件閱讀網站。`index.html` 作為目錄頁，每篇文章為獨立 HTML 檔案。

---

## 目錄結構

```
DocDisplay/
├── index.html            # 目錄頁（列出所有文章）
├── style.css             # 共用樣式
├── articles/             # 各篇文章 HTML
│   ├── article-1.html
│   └── article-2.html
└── Data/
    ├── plan.md           # 本規劃文件
    └── articles.json     # 文章清單（標題、路徑、描述、日期）
```

---

## 頁面說明

### index.html — 目錄頁

- 顯示網站標題與簡介
- fetch 讀取 `Data/articles.json`，動態渲染文章卡片列表
- 每張卡片顯示：標題、日期、摘要
- 點擊卡片或標題連結可進入對應文章頁面

### articles/*.html — 文章頁

- 各自獨立的 HTML 檔案，內容直接硬編碼
- 頁首有網站名稱 + 返回目錄按鈕（`../index.html`）
- 支援 `<h1>`~`<h3>` 標題層級、段落、`<code>` 等基本排版

---

## 資料格式：articles.json

```json
[
  {
    "title": "文章標題",
    "file": "articles/article-1.html",
    "date": "2026-04-27",
    "summary": "文章的一行摘要"
  }
]
```

---

## 樣式方向

- 色調：白底，深灰文字，主色調藍（`#3b82f6`）
- 字體：`JetBrains Mono`（等寬，開發風格）+ 系統 sans-serif 備援
- 版型：單欄置中，最大寬度 `760px`，閱讀友善行距
- 卡片列表：垂直排列，hover 有淡藍底色效果
- 響應式：單欄 mobile-first，桌機維持置中固定寬度

---

## Vue 3 使用範圍

- **index.html**：用 Vue 3 fetch `articles.json` 並渲染卡片列表（`v-for`、`reactive`）
- **文章頁**：純靜態 HTML，不需要 Vue（降低複雜度）

---

## 範例文章

初始建立兩篇範例文章：
1. `articles/getting-started.html` — 「如何開始使用 DocDisplay」
2. `articles/markdown-guide.html` — 「文章格式指南」
