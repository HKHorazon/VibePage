---
name: course-parse-pdf
description: "Course 專案專用 PDF 轉 JSON 技能。使用 pdfplumber 將指定 PDF（教師課表或班級課表）依照使用者說明解析為 schedule.json。Use when: parse pdf, 解析PDF, 轉換課表, pdf to json, convert schedule, 更新課表資料。"
---

# course-parse-pdf — PDF 解析轉 JSON

## 觸發與參數

使用者呼叫時應提供：
- **教師課表 PDF 路徑**（必填）：例如 `Course/data/1142多遊系教師課表.pdf`
- **班級課表 PDF 路徑**（必填）：例如 `Course/data/班級課表.pdf`
- **轉換說明**（選填）：若有額外的欄位規則或過濾條件

若使用者未提供轉換說明，依下方「預設規則」執行。

**中間產物路徑（固定）**：
- `Course/data/schedule_teacher.json` — 教師課表解析結果
- `Course/data/schedule_class.json` — 班級課表解析結果

**最終輸出路徑（固定）**：
- `Course/src/schedule.json` — 兩份合成後的最終課表

---

## 執行流程

### 步驟 1：探查 PDF 結構

先用 Python 探查 PDF，取得頁數、表格結構、範例儲存格，讓後續解析有正確依據：

```bash
cd d:/VibePage
python - <<'EOF'
import pdfplumber, json, unicodedata, warnings
warnings.filterwarnings('ignore')

PDF_PATH = '<使用者指定路徑>'

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

with pdfplumber.open(PDF_PATH) as pdf:
    print(f'頁數: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages[:3]):
        print(f'\n--- 第 {i+1} 頁 ---')
        text = nfc(page.extract_text() or '')
        print('文字前300字:', text[:300])
        tables = page.extract_tables() or []
        print(f'表格數: {len(tables)}')
        if tables:
            tbl = tables[0]
            print(f'表格大小: {len(tbl)} 列 × {len(tbl[0]) if tbl else 0} 欄')
            print('前3列:')
            for row in tbl[:3]:
                print(' ', [nfc(str(c) if c else '') for c in row])
EOF
```

根據探查結果，確認：
- 每頁對應的主體（班級名稱或老師姓名的提取方式）
- 表格的列索引 → 節次對照
- 表格的欄索引 → 星期對照
- 儲存格內文字的排列結構（課程/老師/教室 的順序）

### 步驟 2：確認轉換規則

若使用者有提供轉換說明，以使用者說明為準。  
若無，使用下方預設規則。

完整轉換規則確認後，向使用者簡短摘要（2～4 行），確認無誤後再繼續。

---

## 預設規則（Course 專案標準格式）

### 輸出 JSON 結構

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

### 節次對照

| 節次原文 | period 值 |
|----------|-----------|
| 第1～第10 | `"1"`～`"10"` |
| 第A～第D | `"A"`～`"D"` |
| 中午 | **略過** |

### 星期對照

| 原文 | day 值 |
|------|--------|
| 星期一 | `"一"` |
| 星期二 | `"二"` |
| 星期三 | `"三"` |
| 星期四 | `"四"` |
| 星期五 | `"五"` |

### 儲存格文字合併（join_lines）

PDF 提取文字常有斷行，合併規則：
- 中文接中文：直接相接，不加空格
- 英數接中文 / 中文接英數：直接相接
- 英數接英數：加一個空格

### 欄位拆分（parse_cell）

以教室代碼 regex `[A-Z]{1,5}\d{3,4}` 為分隔點：
- 教室代碼前 → `course`
- 教室代碼本身 → `room`
- 教室代碼後 → `class`

若無教室代碼：嘗試找 `日四技` / `夜四技` 作為 class 起始點；若都找不到，整段當 course，room / class 為空字串。

### 選修標記（optional）

若 `course` 欄位含有 `(*)` 或 `*`：
- 將其從課程名稱中移除（例如 `(*)光雕投影藝術創作` → `光雕投影藝術創作`）
- 在該筆記錄加入 `"optional": true`
- 無標記的課程不加此欄位

### CJK 部首字元處理

PDF 中的中文字有時使用 CJK Radicals Supplement（U+2F00–U+2FD5）而非標準漢字（U+4E00–U+9FFF）：
- **星期偵測**：對欄標題使用 NFKC 正規化後再比對 `星期一～五`，避免 ⼀（U+2F00）無法匹配 一（U+4E00）
- **老師名字 regex**：`^[\u4e00-\u9fff\u2f00-\u2fd5]{2,3}$`（含部首字元範圍）
- **教室代碼**：允許行末有額外文字（如 `MB208院共同時段`），用 `^[A-Z]{1,5}\d{3,4}` 前綴匹配，只擷取代碼部分

### CJK 部首字元處理

PDF 中的中文字有時使用 CJK Radicals Supplement（U+2F00–U+2FD5）而非標準漢字（U+4E00–U+9FFF）：
- **星期偵測**：欄標題使用 NFKC 正規化後再比對 `星期一～五`，避免 ⼀（U+2F00）≠ 一（U+4E00）
- **老師名字 regex**：`^[\u4e00-\u9fff\u2f00-\u2fd5]{2,3}$`（含部首字元範圍）
- **教室代碼**：允許行末有額外文字（如 `MB208院共同時段`），改用前綴匹配 `^[A-Z]{1,5}\d{3,4}`

### 略過規則

- 空格、空白儲存格
- 含 `Office Hours` 的格子
- `中午` 節次列
- 僅含星期標頭文字的格子（第1節與表頭合併的 PDF 格式）
- 含 `院共同時段`、`課外活動` 的格子
- 僅含星期標頭文字（`星期一`～`星期五`）的格子（第1節列與表頭合併的 PDF 格式）
- 含 `院共同時段`、`課外活動`、`體育` 的格子

---

### 教師課表（每頁一位老師）

**識別方式**：頁面左上角出現 `授課教師：{姓名}` 或 `[授課教師]：{姓名}` 字樣。

- `teacher`：從頁面 header 提取 `授課教師` 後的姓名，整頁所有筆記都套用此值
- 橫軸 = 星期（從欄標題讀取 `星期一`～`星期五`）
- 縱軸 = 節次（從列標題讀取 `1`～`10`、`A`～`D`；中午略過）

**儲存格欄位解析順序**（行由上到下）：
1. **`course`**：課程名稱，可能跨多行；將多行依 `join_lines` 規則合併
2. **`room`**：包含英文字母與數字的教室代碼，例如 `M202`、`MB208`；通常出現在中段
3. **`class`**：通常是最後兩行合併而成（例如 `日四技多遊` + `系2年乙班` → `日四技多遊系2年乙班`）

**解析策略**：
- 先從所有行中找出符合 `^[A-Z]{1,5}\d{3,4}$` 的行作為 `room`
- room 之後的所有行合併為 `class`（若 room 是倒數第2行，最後1行為 class；若 room 之後有2行則合併）
- room 之前的所有行合併為 `course`（用 `join_lines` 規則）
- 若找不到 room：嘗試用 `日四技` / `夜四技` 判斷 class 起始點；若都無，整段為 course，room / class 為空字串

**略過規則（教師課表額外）**：
- 含 `Office Hours` 的儲存格
- 儲存格文字全為空白或 `None`

### 班級課表（每頁一個班級）

**識別方式**：頁面左上角出現 `班級：{名稱}` 或 `[班級]：{名稱}` 字樣。

- `class`：從頁面 header 提取 `班級` 後的名稱，整頁所有筆記都套用此值
- 橫軸 = 星期（從欄標題讀取 `星期一`～`星期五`）
- 縱軸 = 節次（從列標題讀取 `1`～`10`、`A`～`D`；中午略過）

**儲存格欄位解析順序**（行由上到下）：
1. **`course`**：課程名稱，偶爾跨行；將多行依 `join_lines` 規則合併（room 和 teacher 之前的所有行）
2. **`teacher`**：通常為第二行（2～3 個中文字的姓名）；也可由下往上找：room 的前一行
3. **`room`**：包含英文字母與數字的教室代碼，例如 `M202`、`MB208`；通常是最後一行

**解析策略**：
- 若行首為 `星期[一二三四五]`（NFKC 比對），去除該行（第1節列與表頭合併的格式）
- 先從所有行中找出以 `^[A-Z]{1,5}\d{3,4}` 開頭的行作為 `room`（只取前綴代碼，忽略後綴文字如 `院共同時段`）
- 從 room 往前找，跳過 `...` 行，找到第一個符合 `^[\u4e00-\u9fff\u2f00-\u2fd5]{2,3}$` 的行作為 `teacher`
- teacher 之前所有行（跳過 `...`）合併為 `course`（用 `join_lines` 規則）
- 若找不到 room：略過此儲存格，但列入「無法解析格子」清單回報
- 若找不到 teacher：`teacher` 設為空字串，仍保留此筆記錄

### 無法解析格子的回報規則

解析完成後，若有格子**不是空白、不是特殊文字**（院共同時段、Office Hours、課外活動），但因無教室代碼或其他原因被略過，**必須向使用者回報**：

```
以下格子無法解析，請確認是否遺漏：
  [班級] 星期X 第N節：{原始文字}
```

讓使用者以「老師 / 班級 / 第幾天第幾節」格式決定是否補資料。

---

## 兩份 PDF 的重複處理策略

教師課表與班級課表**同時提供**時，會有重複資料。處理原則：

**執行順序**：先解析教師課表建立基礎資料，再用班級課表補漏或修正。

**去重鍵**：以 `(teacher, day, period)` 為複合 key。

| 情況 | 處理方式 |
|------|----------|
| key 相同、所有欄位一致 | 保留一筆，不重複寫入 |
| key 相同、欄位有差異 | 保留教師課表的版本；若教師課表該欄位為空字串，則以班級課表補值 |
| 班級課表有、教師課表無 | 新增（補漏） |

**班級課表額外過濾規則**：
- room 不存在 → 略過
- teacher 不在 `src/teachers.json` 中**不略過**，仍保留（收錄所有多遊系課程）

---

## 步驟 3：撰寫並執行教師課表解析腳本

在 `Course/data/` 產生一次性腳本 `parse_teacher_temp.py`：
- 輸入：教師課表 PDF
- 輸出：`Course/data/schedule_teacher.json`
- 使用 `pdfplumber`、`json`、`re`、`unicodedata`
- stdout 輸出：頁數、解析筆數、略過筆數

```bash
cd d:/VibePage
python Course/data/parse_teacher_temp.py
```

執行失敗時讀取錯誤訊息、修正、重試（最多 3 次）。  
成功後刪除腳本：`rm Course/data/parse_teacher_temp.py`

---

## 步驟 4：撰寫並執行班級課表解析腳本

在 `Course/data/` 產生一次性腳本 `parse_class_temp.py`：
- 輸入：班級課表 PDF
- 輸出：`Course/data/schedule_class.json`
- 同上規格

```bash
cd d:/VibePage
python Course/data/parse_class_temp.py
```

執行失敗時同樣重試。  
成功後刪除腳本：`rm Course/data/parse_class_temp.py`

---

## 步驟 5：合成最終 schedule.json

產生一次性腳本 `merge_temp.py`，合成兩份中間 JSON：

```python
# 讀取兩份中間產物
teacher_data = json.load(open('Course/data/schedule_teacher.json', encoding='utf-8'))
class_data   = json.load(open('Course/data/schedule_class.json',   encoding='utf-8'))

# 以 (teacher, day, period) 為複合 key 去重
# 1. 先放入教師課表所有資料
# 2. 逐筆處理班級課表：
#    - key 已存在 → 若教師課表某欄位為空字串，則以班級課表補值；否則保留教師課表版本
#    - key 不存在 → 新增（補漏）
# 輸出到 Course/src/schedule.json
```

```bash
cd d:/VibePage
python Course/data/merge_temp.py
```

成功後刪除：`rm Course/data/merge_temp.py`

---

## 步驟 6：驗證最終結果

```bash
cd d:/VibePage
python - <<'EOF'
import json
t = json.load(open('Course/data/schedule_teacher.json', encoding='utf-8'))
c = json.load(open('Course/data/schedule_class.json',   encoding='utf-8'))
s = json.load(open('Course/src/schedule.json',          encoding='utf-8'))
print(f'教師課表: {len(t)} 筆')
print(f'班級課表: {len(c)} 筆')
print(f'合成結果: {len(s)} 筆')
teachers = sorted(set(x["teacher"] for x in s if x["teacher"]))
print(f'老師數: {len(teachers)}，{teachers}')
print('前3筆:', s[:3])
EOF
```

---

## 步驟 7：回報結果

```
✓ 解析完成
  教師課表 → Course/data/schedule_teacher.json（X 筆）
  班級課表 → Course/data/schedule_class.json（X 筆）
  合成結果 → Course/src/schedule.json（X 筆，老師 X 位）
```

若有資料品質問題（room 為空、teacher 未識別等），列在摘要後讓使用者決定是否處理。

---

## 注意事項

- 所有路徑以 `d:/VibePage/` 為根，Python 腳本中用 `Course/data/...` 相對路徑開啟檔案
- pdfplumber 需已安裝（`pip install pdfplumber`），若未安裝則先安裝
- 產生的腳本是一次性的，執行成功後刪除
- 不修改 `src/teachers.json`，只讀取做過濾用
