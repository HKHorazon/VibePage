---
name: ship
description: "VibeWeb 一鍵部署技能。推送最新變更到 GitHub（https://github.com/HKHorazon/VibePage.git），顯示 GitHub Pages 連結，並同時啟動本地 HTTP server 顯示本地連結。Use when: deploy, ship, 推送, 部署, 上線, 發布。"
---

# Ship — VibeWeb 一鍵部署

執行此 skill 時，依序完成以下步驟：

## 步驟 1：推送到 GitHub

1. 執行 `git status` 確認目前變更
2. 執行 `git add -A` 暫存所有變更
3. 若有變更，詢問使用者 commit message（或建議一個簡短的訊息）
4. 執行 `git commit -m "<message>"` 建立 commit
5. 執行 `git push origin main`（若 remote 不存在則先執行 `git remote add origin https://github.com/HKHorazon/VibePage.git`）
6. 若目前 branch 不是 main，改用目前 branch 名稱

## 步驟 2：顯示 GitHub Pages 連結

push 完成後輸出：

```
🚀 已推送到 GitHub！

🌐 GitHub Pages：https://hkhorazon.github.io/VibePage/
   （GitHub Pages 通常在 1～2 分鐘內更新）
```

## 步驟 3：啟動本地伺服器

在背景啟動本地 HTTP server，優先使用 Python，其次 Node.js：

```bash
# 優先嘗試 Python
python -m http.server 8080

# 若 Python 不可用，改用 Node.js
npx serve -l 8080 .
```

啟動後輸出：

```
💻 本地伺服器：http://localhost:8080/
   子專案直接加路徑，例如：http://localhost:8080/HungAi/
```

## 注意事項

- 若 `git status` 顯示 nothing to commit，跳過 commit 步驟，直接顯示連結並啟動本地伺服器
- 若 push 失敗（例如 remote 不存在或權限問題），明確告知錯誤並停止，不要強制操作
- 本地伺服器以 background 模式啟動，不阻塞對話
