---
name: ship-local
description: "VibeWeb 本地伺服器技能。啟動本地 HTTP server 並顯示所有子專案的本地連結。Use when: 本地預覽, 啟動伺服器, local server, local, 看本地, 預覽。"
---

# Ship-Local — 啟動本地伺服器

執行此 skill 時，依序完成以下步驟：

## 步驟 1：偵測可用的伺服器工具

依序嘗試以下指令，找到第一個可用的：

1. `python --version` 或 `python3 --version`
2. `node --version`

## 步驟 2：選擇 Port

Port 範圍固定為 **8080～8089**，每次必須選一個與上次不同的 port：

1. 執行 `netstat -ano | findstr :808` 查看目前哪些 port 已被佔用
2. 從 8080～8089 中選一個**目前未被使用**的 port
3. 若所有 port 都被佔用，告知使用者

目的是強制瀏覽器視為新連線，避免快取問題。

## 步驟 3：啟動本地 HTTP server

在 VibeWeb 根目錄以 **background 模式**啟動伺服器，優先 Python，其次 Node.js：

```bash
# 優先嘗試 Python（PORT 為上一步選定的 port）
python -m http.server <PORT>

# 若 Python 不可用，改用 Node.js
npx serve -l <PORT> .
```

- 確認伺服器成功啟動後再顯示連結

## 步驟 4：顯示連結表格

伺服器啟動後，掃描根目錄下有 `index.html` 的子資料夾（排除 `framework/`），列出所有子專案：

```
本地伺服器已啟動！

| 專案    | 本地連結                          |
|---------|-----------------------------------|
| HungAi  | http://localhost:8080/HungAi/     |
| Course  | http://localhost:8080/Course/     |
```

> 動態偵測根目錄下的子資料夾，有 `index.html` 就列入表格。

## 注意事項

- 伺服器以 background 模式啟動，不阻塞對話
- 若兩種工具都不可用，告知使用者安裝 Python 或 Node.js
- 不執行任何 git 操作
