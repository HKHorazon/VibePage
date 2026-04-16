# schedule.json 轉換規則

## 來源

`data/1142多遊系教師課表.pdf`（11頁，每頁一位老師）

## 工具

- Python `pdfplumber`：提取 PDF 表格
- 自訂解析函式：拆解每格的課程、教室、班級

---

## 轉換流程

```
PDF → pdfplumber.extract_tables() → 原始 table (list of rows)
  → 每格文字（含 \n 斷行）
  → join_lines() 合併斷字
  → parse_cell() 拆出 course / room / class
  → flat array JSON
```

---

## JSON 結構（src/schedule.json）

Flat array，每筆代表一個課程時段：

```json
[
  {
    "teacher": "楊國隆",
    "day": "一",
    "period": "2",
    "course": "專案管理",
    "room": "MB208",
    "class": "日四技多遊系2年乙班"
  }
]
```

| 欄位 | 說明 | 範例值 |
|------|------|--------|
| `teacher` | 老師姓名 | `楊國隆` |
| `day` | 星期（一～五） | `一` |
| `period` | 節次 | `1`～`8`、`A`～`D` |
| `course` | 課程名稱 | `專案管理`、`(*)基礎遊戲製作` |
| `room` | 教室代碼 | `MB208`、`G501`、`EB101` |
| `class` | 班級資訊 | `日四技多遊系2年乙班` |

---

## 解析規則

### 1. 節次（period）對照

| PDF 原文 | JSON period |
|----------|-------------|
| 第1～第8 | `1`～`8` |
| 第A～第D | `A`～`D` |
| 中午 | 略過（不含課程） |
| 第9、第10 | 略過（plan.md 規格不含） |

### 2. 星期（day）對照

| PDF 原文 | JSON day |
|----------|----------|
| 星期一 | `一` |
| 星期二 | `二` |
| 星期三 | `三` |
| 星期四 | `四` |
| 星期五 | `五` |

### 3. 儲存格合併（join_lines）

PDF 提取的文字常在中文詞中間斷行，例如：
```
產品⾏
銷 M203
⽇四技多遊
系1年⼄班
```

合併規則：
- 中文接中文：直接相接，**不加空格**
- 英數接中文 / 中文接英數：直接相接
- 英數接英數：加一個空格

結果：`產品行銷 M203 日四技多遊系1年乙班`

### 4. 欄位拆分（parse_cell）

合併後文字，用教室代碼 regex `[A-Z]{1,5}\d{3,4}` 當分隔點：
- 教室代碼**前**的文字 = `course`
- 教室代碼本身 = `room`
- 教室代碼**後**的文字 = `class`

若無教室代碼：
- 嘗試找 `日四技` / `夜四技` 作為 class 起始點
- 若都找不到：整段當 course，room 和 class 為空字串

### 5. 略過的儲存格

- 空格或空白
- 含 `Office Hours` 的格子

---

## 重新產生方式

```bash
python << 'EOF'
# 執行 d:/VibeWeb/Course/data/ 內的 convert.py（若有）
# 或手動執行當時使用的 Python 腳本
EOF
```

> 若 PDF 更新，重新執行解析腳本即可覆蓋 `src/schedule.json`。
