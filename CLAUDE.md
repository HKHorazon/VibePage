# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 回覆風格

直接給結果，不要前言、不要總結。使用工具後只回報結果，不描述過程。除非使用者主動問，否則不解釋在做什麼。程式碼保持完整，其他回覆保持簡短。

使用者可以用任何語言提問，但回覆一律使用**繁體中文**。

若執行過程中發現潛在的錯誤、漏洞或效能問題，在結果後簡短列出，讓使用者決定是否處理。

## 專案概述

VibeWeb 是一個**純靜態網頁專案集**，不使用任何建置工具、打包器或套件管理器。所有網頁直接在瀏覽器中運行，無需編譯步驟。

- **GitHub Repo**：https://github.com/HKHorazon/VibePage.git
- **部署平台**：GitHub Pages（所有功能必須在 GitHub Pages 環境下正常運作）

## 專案結構

- `framework/` — 共用前端框架資源（Vue 3 ESM、Tailwind CSS），所有子專案共用
- 其餘每個子資料夾為一個獨立靜態網頁專案，資料夾慣例如下：
  - `data/` — 內部規劃文件與原始資料（不供網頁程式存取）
  - `src/` — 網頁可存取的靜態資源，如圖片、JSON/XML 資料檔等

## 技術架構

### 無建置工具開發
- **Vue 3**：透過 `<script type="module">` 直接載入 ESM 版本，使用 `createApp` + `setup()` Composition API
- **Tailwind CSS**：本地靜態檔案，不使用 CDN
- **CSS**：Tailwind 負責 utility classes，`style.css` 負責自訂元件樣式（CSS variables + BEM-like 命名）
- 框架資源統一放在 `../framework/`，以相對路徑引用

### 資料管理
- 簡單內容直接硬編碼在 `index.html` 的 Vue `setup()` 函式內的 `reactive()` 物件
- 較複雜或獨立的資料會放在子專案的 `res/` 資料夾，以 JSON 或 XML 等格式儲存，並由前端非同步載入
- `Data/*.md` 檔案是**內容規劃文件**，供開發參考，不由網頁程式讀取

### 響應式版面
- 手機：1 欄（< 560px）
- 平板：2 欄（560px–899px）
- 桌機：3 欄（≥ 900px）
- 九大項目的展開邏輯依欄數同步開關同列所有卡片（見 `toggleItem` 函式）

## GitHub Pages 限制

部署在 GitHub Pages 上，開發時須遵守以下限制：
- **只能使用靜態資源**：無伺服器端執行、無後端 API
- **fetch 資料檔**：讀取 `res/` 內的 JSON/XML 時，需透過 HTTP server 執行（本地直接開啟 `file://` 會被 CORS 擋住），GitHub Pages 上則正常
- **路徑使用相對路徑**：避免以 `/` 開頭的絕對路徑，否則在 GitHub Pages 的子路徑部署下會失效
- **不可使用 localStorage / Service Worker 以外的持久化**：GitHub Pages 無資料庫

## 新增子專案規範

每個子專案為獨立資料夾，放在專案根目錄下：
- 引用共用框架使用 `../framework/vue.esm-browser.js` 和 `../framework/tailwind.min.css`
- 各自管理自己的 `style.css` 與 `data/` 資料夾
- 不建立 `package.json`、`node_modules` 或任何建置設定檔

## 開發方式

直接用瀏覽器開啟 HTML 檔案，或啟動一個簡易 HTTP server（避免 CORS 問題）：

```bash
# Python（若已安裝）
python -m http.server 8080

# Node.js（若已安裝）
npx serve .
```

沒有 lint、test、build 指令。
