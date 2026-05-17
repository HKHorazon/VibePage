---
name: vibe-page
description: 在 VibePage 專案中建立新的靜態網頁子專案。詢問功能、風格、RWD、資料格式等需求後，產生完整的 index.html + style.css 腳手架，符合本專案的 Vue 3 ESM + Tailwind 純靜態架構。Use when: 新增子專案, 建立新頁面, new subproject, create static page, scaffold, /vibe-page。每次使用者想在 VibePage 底下新增任何網頁功能時都應觸發此 skill。
argument-hint: "新子專案名稱（可選，例如 MyTool）"
---

# vibe-page — VibePage 子專案建立器

## 專案慣例速查

```
VibePage/
├── framework/
│   ├── vue.esm-browser.js   ← Vue 3 ESM（相對路徑 ../framework/）
│   └── tailwind.min.css     ← Tailwind（相對路徑 ../framework/）
└── <ProjectName>/
    ├── index.html
    ├── style.css
    ├── data/                ← 規劃文件（不供網頁存取）
    └── src/                 ← 網頁可存取的靜態資源（JSON、圖片等）
```

- 所有路徑用**相對路徑**，不可用 `/` 開頭
- 不建立 package.json / node_modules / build 設定
- GitHub Pages 限制：純靜態，無後端 API

---

## 流程

### Step 1 — 訪談

用**一次訊息**列出以下問題，請使用者回答（可部分跳過）：

```
請描述這個新子專案：

1. **資料夾名稱**：英文 PascalCase（例如 MyTool）
2. **主要功能**：這個頁面要做什麼？有哪些互動元素？
3. **視覺風格**：
   - 暗色科技感（類似 Course：深黑底、青色霓虹）
   - 清爽明亮（淺色、白底、低飽和）
   - 自訂：請描述主色調與氛圍
4. **版面類型**：
   - 全螢幕固定（100dvh，不捲動，類似 Course）
   - 可捲動頁面（內容展開，類似 DocDisplay）
5. **RWD 需求**：
   - 手機優先（mobile-first，主要在手機使用）
   - 雙模式（手機 + 桌機，有明顯排版差異）
   - 純桌機（不需特別優化手機）
6. **資料來源**：
   - 全部硬編碼在 HTML（不需 fetch）
   - 讀取 src/ 內的 JSON（非同步 fetch）
   - 內嵌 HTML 文章（fetch 獨立 .html 檔案，以 v-html 渲染；適合文章、教學，可含圖表）
   - Google Sheets CSV（試算表公開發布為 CSV，fetch 後解析）
   - 混合（部分硬編碼、部分 fetch）
7. **額外元件**（可多選）：
   - 全螢幕蓋層 / Modal
   - 搜尋 / 篩選功能
   - 排序功能
   - 無
```

等使用者回答後再進 Step 2。

---

### Step 2 — 輸出規劃摘要

根據回答，用繁體中文輸出：

```
## 建立規劃

**專案**：ProjectName/
**風格**：〔簡述〕
**版面**：〔全螢幕 / 捲動〕
**RWD**：〔策略〕

### CSS Variables 預設
--bg / --surface / --accent / --text 的預設值

### HTML 結構
- header / main / footer 等區塊說明

### Vue setup() 大綱
- reactive 狀態列表
- computed 列表
- 主要 function 列表
- onMounted 非同步載入（若需要）

### 資料結構（若需要 fetch）
- JSON：列出 src/ 的檔名與 schema
- Google Sheets：列出試算表欄位與解析策略
```

詢問使用者確認，或要求修改。

---

### Step 3 — 建立檔案

確認後，建立以下檔案：

#### 3a. 資料夾結構

```bash
mkdir -p "d:/Projects_Others/VibePage/<ProjectName>/src"
mkdir -p "d:/Projects_Others/VibePage/<ProjectName>/data"
```

#### 3b. index.html

**必要結構**（依訪談結果填入）：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><!-- 專案標題 --></title>
  <link rel="stylesheet" href="../framework/tailwind.min.css">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <div id="app" v-cloak>
    <!-- 依規劃輸出的 HTML 結構 -->
  </div>

  <script type="module">
    import { createApp, ref, reactive, computed, onMounted } from '../framework/vue.esm-browser.js'

    createApp({
      setup() {
        // 依規劃輸出的 Vue setup 內容

        return { /* 所有需暴露給模板的狀態與方法 */ }
      }
    }).mount('#app')
  </script>
</body>
</html>
```

**重要原則**：
- `[v-cloak] { display: none; }` 必須在 style.css 中加入，避免 FOUC
- 若有 fetch，用 `onMounted(async () => { try { ... } catch(e) {} })` 包住
- 本地 JSON 路徑用 `./src/xxx.json`，fetch 後 `.then(r => r.json())`
- Google Sheets CSV 路徑見下方說明

#### 3c. style.css

**必要結構**：

```css
/* ── CSS Variables ─────────────────────── */
:root {
  /* 依訪談結果定義 --bg、--surface、--accent、--text 等變數 */
}

* { box-sizing: border-box; margin: 0; padding: 0; }
[v-cloak] { display: none; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: /* 依風格選字體 */;
  /* 全螢幕：height: 100dvh; overflow: hidden; */
  /* 捲動：min-height: 100dvh; */
}

/* 依各元件需求補充 */
```

**風格參考**：
- 暗色科技感：`--bg: #090912`、`--accent: #00e5ff`、使用 `JetBrains Mono` 或 `Chakra Petch`（Google Fonts）、box-shadow 霓虹效果
- 清爽明亮：`--bg: #f8fafc`、`--accent: #3b82f6`、使用 `system-ui` 或 `Inter`、圓角 border-radius、低飽和陰影

#### 3d. src/xxx.json（若資料來源為本地 JSON）

建立空的 JSON 骨架，schema 依訪談結果。

---

## 內嵌 HTML 文章模式

適合文章、教學、說明文件等需要富文本內容（含圖表、表格、程式碼區塊）的場景。

### 結構

```
ProjectName/
├── src/
│   ├── articles.json          ← 文章清單與 metadata
│   └── articles/
│       ├── intro.html         ← 各篇內容（純 HTML 片段）
│       └── topic-a.html
```

`articles.json` 建議 schema：
```json
[
  { "slug": "intro", "title": "...", "desc": "...", "tags": ["入門"] }
]
```

### fetch + v-html 渲染

```javascript
const articleHtml = ref('')
const loading = ref(false)

async function selectArticle(slug) {
  loading.value = true
  try {
    const res = await fetch(`./src/articles/${slug}.html`)
    articleHtml.value = await res.text()
  } catch(e) {
    articleHtml.value = '<p>載入失敗</p>'
  } finally {
    loading.value = false
  }
}
```

模板：
```html
<div class="article-body" v-html="articleHtml"></div>
```

### 各 .html 文章注意事項

- 只寫**片段**，不含 `<html>/<head>/<body>` 標籤
- 可自由使用 `<h2>`、`<p>`、`<table>`、`<figure>`、`<pre>`、`<code>`、行內 `<script>`（圖表 library）
- 行內 `<script>` 在 `v-html` 中**不會自動執行**；若需執行圖表初始化，需在 `selectArticle` 後用 `nextTick` + 動態插入 script 節點
- style 請用文章共用的 `.article-body` CSS 後代選擇器管理，避免污染全域

---

## Google Sheets 資料來源

### 設定方式

試算表必須「發布到網路」才能跨域 fetch：
1. 試算表 → 檔案 → 共用 → 發布到網路
2. 選擇工作表 → 格式選 **CSV** → 發布
3. 取得 URL（格式如下）

```
https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv&gid=<GID>
```

- `SHEET_ID`：試算表網址中 `/d/` 後的那段
- `GID`：底部工作表標籤的 `gid` 參數（第一張預設為 0）

### fetch + 解析範本

不需引入外部套件，直接手動解析 CSV：

```javascript
onMounted(async () => {
  try {
    const SHEET_URL = 'https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=0'
    const res = await fetch(SHEET_URL)
    const text = await res.text()
    const rows = text.trim().split('\n').map(row =>
      row.split(',').map(cell => cell.trim().replace(/^"|"$/g, ''))
    )
    const headers = rows[0]
    const items = rows.slice(1).map(row =>
      Object.fromEntries(headers.map((h, i) => [h, row[i] ?? '']))
    )
    data.items = items
  } catch(e) {
    console.error('試算表載入失敗', e)
  }
})
```

> **注意**：若儲存格內容含逗號或換行，需改用更完整的 CSV parser（可引入 PapaParse CDN）。

### PapaParse（選用，處理複雜 CSV）

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5/papaparse.min.js"></script>
```

```javascript
const res = await fetch(SHEET_URL)
const text = await res.text()
const { data: rows } = Papa.parse(text, { header: true, skipEmptyLines: true })
data.items = rows
```

### 本地開發注意

Google Sheets CSV URL 是跨域請求，`file://` 下會被 CORS 擋住。
需啟動 HTTP server：`/ship-local`

---

## 完成提示

```
✓ ProjectName/ 建立完成

檔案：
  index.html
  style.css
  src/（若有）
  data/

本地預覽：/ship-local
部署：/ship
```

---

## 品質檢查清單

建立完成後，自我確認：
- [ ] `[v-cloak]` 樣式已加入 style.css
- [ ] 所有 `../framework/` 路徑正確（相對路徑，不以 `/` 開頭）
- [ ] fetch 有 try/catch
- [ ] RWD media query 或 Tailwind 響應式 class 已實作
- [ ] Vue `return {}` 包含所有模板用到的狀態與方法
- [ ] Google Sheets：URL 已替換為實際 SHEET_ID / GID
- [ ] GitHub Pages 限制：無後端依賴

---

## 常見風格片段

### 暗色霓虹按鈕
```css
.btn {
  background: var(--surface);
  border: 1px solid var(--accent);
  color: var(--accent);
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.15);
  transition: box-shadow 0.12s, background 0.12s;
}
.btn:hover {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  box-shadow: 0 0 18px rgba(0, 229, 255, 0.3);
}
```

### 掃描線覆蓋效果（暗色科技感）
```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent, transparent 2px,
    rgba(0, 229, 255, 0.018) 2px, rgba(0, 229, 255, 0.018) 4px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### 全螢幕蓋層
```css
.overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-direction: column;
  background: rgba(0, 0, 10, 0.75);
  backdrop-filter: blur(6px);
}
```

### RWD 斷點（配合 CLAUDE.md 規範）
```css
/* 手機：1欄（< 560px）*/
/* 平板：2欄（560px–899px）*/
@media (min-width: 560px) { ... }
/* 桌機：3欄（≥ 900px）*/
@media (min-width: 900px) { ... }
```
