# SyllabusTrack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一個給大學教授使用的課程進度追蹤靜態網頁，支援多門課程、25% 單位進度紀錄、週誌與備註。

**Architecture:** 純靜態 Vue 3 ESM 單頁應用，所有狀態存 `localStorage`。單一 `index.html` + `style.css`，不使用建置工具。進度條三色（灰/藍/綠）依據快照基準即時計算。

**Tech Stack:** Vue 3 ESM (`../framework/vue.esm-browser.js`)、Tailwind CSS (`../framework/tailwind.min.css`)、localStorage、原生 HTML5 drag-and-drop

---

## 檔案結構

| 檔案 | 職責 |
|------|------|
| `SyllabusTrack/index.html` | Vue 3 app 主體，所有元件邏輯（inline script） |
| `SyllabusTrack/style.css` | 自訂樣式：進度條三色、overlay 動畫、sidebar、RWD |

---

## 共用常數與函式（貫穿所有任務）

```javascript
// 產生 UUID
function uuid() {
  return crypto.randomUUID()
}

// localStorage key
const STORAGE_KEY = 'syllabustrack_data'
const SNAPSHOT_PREFIX = 'syllabustrack_snapshot_'

// 進度合法值
const VALID_PROGRESS = [0, 25, 50, 75, 100]

// 載入資料
function loadData() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { courses: [], activeCourseId: null }
  } catch { return { courses: [], activeCourseId: null } }
}

// 儲存資料
function saveData(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

// 載入某課程快照（回傳 { unitId: progress } 物件）
function loadSnapshot(courseId) {
  try {
    return JSON.parse(localStorage.getItem(SNAPSHOT_PREFIX + courseId)) || {}
  } catch { return {} }
}

// 儲存某課程快照
function saveSnapshot(courseId, units) {
  const snap = {}
  units.forEach(u => { snap[u.id] = u.progress })
  localStorage.setItem(SNAPSHOT_PREFIX + courseId, JSON.stringify(snap))
}

// 計算週次
function calcWeekNumber(semesterStart, weeklyLogLength) {
  if (semesterStart) {
    const start = new Date(semesterStart)
    const today = new Date()
    return Math.max(1, Math.floor((today - start) / (7 * 86400000)) + 1)
  }
  return weeklyLogLength + 1
}

// 格式化日期 YYYY/MM/DD
function formatDate(dateStr) {
  return dateStr.replace(/-/g, '/')
}
```

---

## Task 1: 專案骨架 + 資料層

**Files:**
- Create: `SyllabusTrack/index.html`
- Create: `SyllabusTrack/style.css`

- [ ] **Step 1: 建立 `style.css`（空骨架 + CSS variables）**

```css
:root {
  --color-bg: #111827;
  --color-surface: #1f2937;
  --color-border: #374151;
  --color-text: #f9fafb;
  --color-muted: #9ca3af;
  --color-blue: #3b82f6;
  --color-green: #22c55e;
  --color-gray-bar: #374151;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: system-ui, sans-serif;
  min-height: 100vh;
}

[v-cloak] { display: none; }
```

- [ ] **Step 2: 建立 `index.html` 骨架，載入框架，掛載 Vue app**

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SyllabusTrack</title>
  <link rel="stylesheet" href="../framework/tailwind.min.css">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <div id="app" v-cloak>
    <p>{{ activeCourse ? activeCourse.name : '尚無課程' }}</p>
  </div>

  <script type="module">
    import { createApp, ref, reactive, computed, onMounted, nextTick } from '../framework/vue.esm-browser.js'

    function uuid() { return crypto.randomUUID() }
    const STORAGE_KEY = 'syllabustrack_data'
    const SNAPSHOT_PREFIX = 'syllabustrack_snapshot_'

    function loadData() {
      try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { courses: [], activeCourseId: null } }
      catch { return { courses: [], activeCourseId: null } }
    }
    function saveData(data) { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)) }
    function loadSnapshot(courseId) {
      try { return JSON.parse(localStorage.getItem(SNAPSHOT_PREFIX + courseId)) || {} }
      catch { return {} }
    }
    function saveSnapshot(courseId, units) {
      const snap = {}
      units.forEach(u => { snap[u.id] = u.progress })
      localStorage.setItem(SNAPSHOT_PREFIX + courseId, JSON.stringify(snap))
    }
    function calcWeekNumber(semesterStart, logLen) {
      if (semesterStart) {
        const diff = new Date() - new Date(semesterStart)
        return Math.max(1, Math.floor(diff / (7 * 86400000)) + 1)
      }
      return logLen + 1
    }
    function formatDate(d) { return d.replace(/-/g, '/') }
    function todayStr() { return new Date().toISOString().slice(0, 10) }

    createApp({
      setup() {
        const data = reactive(loadData())

        const activeCourse = computed(() =>
          data.courses.find(c => c.id === data.activeCourseId) || null
        )

        function persist() { saveData(data) }

        onMounted(() => {
          if (!data.activeCourseId && data.courses.length) {
            data.activeCourseId = data.courses[0].id
          }
        })

        return { data, activeCourse, persist, uuid, loadSnapshot, saveSnapshot, calcWeekNumber, formatDate, todayStr }
      }
    }).mount('#app')
  </script>
</body>
</html>
```

- [ ] **Step 3: 用瀏覽器開啟 `http://localhost:8080/SyllabusTrack/`，確認頁面載入無 console 錯誤，顯示「尚無課程」**

- [ ] **Step 4: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 初始骨架 + 資料層"
```

---

## Task 2: 課程管理（新增、切換、刪除、改名）

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 在 `setup()` 加入課程管理函式**

在 `persist()` 之後加入：

```javascript
// 課程管理
function addCourse() {
  const name = prompt('課程名稱：')
  if (!name || !name.trim()) return
  const c = { id: uuid(), name: name.trim(), units: [], weeklyLog: [] }
  data.courses.push(c)
  data.activeCourseId = c.id
  persist()
}

function renameCourse(course) {
  const name = prompt('新課程名稱：', course.name)
  if (!name || !name.trim()) return
  course.name = name.trim()
  persist()
}

function deleteCourse(course) {
  if (!confirm(`確定刪除「${course.name}」及所有資料？`)) return
  const idx = data.courses.findIndex(c => c.id === course.id)
  data.courses.splice(idx, 1)
  localStorage.removeItem(SNAPSHOT_PREFIX + course.id)
  data.activeCourseId = data.courses.length ? data.courses[0].id : null
  persist()
}

function selectCourse(id) {
  data.activeCourseId = id
  persist()
}

// 學期設定（存在 data 本身）
if (!data.semesterStart) data.semesterStart = ''
const semesterStart = computed({
  get: () => data.semesterStart,
  set: v => { data.semesterStart = v; persist() }
})

const currentWeek = computed(() => {
  if (!activeCourse.value) return null
  return calcWeekNumber(data.semesterStart, activeCourse.value.weeklyLog.length)
})
```

並加入 return：`addCourse, renameCourse, deleteCourse, selectCourse, semesterStart, currentWeek`

- [ ] **Step 2: 桌機頂部 HTML（下拉選單）**

將 `<div id="app">` 內容替換為：

```html
<div id="app" v-cloak>
  <!-- 頂部導覽 -->
  <header class="app-header">
    <!-- 桌機：下拉選單 -->
    <div class="course-dropdown-wrap" v-if="!isMobile">
      <button class="course-dropdown-btn" @click="dropdownOpen = !dropdownOpen">
        {{ activeCourse ? activeCourse.name : '選擇課程' }} ▾
      </button>
      <div v-if="dropdownOpen" class="course-dropdown-menu" @click.stop>
        <div
          v-for="c in data.courses" :key="c.id"
          class="course-dropdown-item"
          :class="{ active: c.id === data.activeCourseId }"
          @click="selectCourse(c.id); dropdownOpen = false"
        >
          <span>{{ c.name }}</span>
          <span class="course-item-actions">
            <button @click.stop="renameCourse(c)">✏️</button>
            <button @click.stop="deleteCourse(c)">🗑️</button>
          </span>
        </div>
        <div class="course-dropdown-add" @click="addCourse(); dropdownOpen = false">＋ 新增課程</div>
      </div>
    </div>
    <!-- 手機：漢堡 + 課程名稱 -->
    <template v-else>
      <button class="hamburger-btn" @click="sidebarOpen = true">☰</button>
      <span class="mobile-course-name">{{ activeCourse ? activeCourse.name : '選擇課程' }}</span>
    </template>
    <!-- 週次標示 -->
    <span v-if="currentWeek && activeCourse" class="week-badge">第 {{ currentWeek }} 週</span>
    <!-- 編輯按鈕 -->
    <button v-if="activeCourse && !editMode" class="edit-btn" @click="editMode = true">✏️</button>
    <button v-if="editMode" class="edit-btn edit-btn--done" @click="editMode = false">完成編輯</button>
  </header>

  <!-- 手機側欄 -->
  <div v-if="sidebarOpen" class="sidebar-backdrop" @click="sidebarOpen = false">
    <div class="sidebar" @click.stop>
      <div class="sidebar-title">課程列表</div>
      <div
        v-for="c in data.courses" :key="c.id"
        class="sidebar-item"
        :class="{ active: c.id === data.activeCourseId }"
        @click="selectCourse(c.id); sidebarOpen = false"
      >
        <span>{{ c.name }}</span>
        <span class="course-item-actions">
          <button @click.stop="renameCourse(c)">✏️</button>
          <button @click.stop="deleteCourse(c)">🗑️</button>
        </span>
      </div>
      <div class="sidebar-add" @click="addCourse()">＋ 新增課程</div>
      <div class="sidebar-semester">
        <label>學期開始日</label>
        <input type="date" v-model="semesterStart" class="semester-input">
      </div>
    </div>
  </div>

  <!-- 主體佔位（後續任務填入） -->
  <main class="app-main">
    <div v-if="!activeCourse" class="empty-state">
      請先新增課程
    </div>
  </main>
</div>
```

在 `setup()` 加入：

```javascript
const isMobile = ref(window.innerWidth < 560)
const dropdownOpen = ref(false)
const sidebarOpen = ref(false)
const editMode = ref(false)

window.addEventListener('resize', () => { isMobile.value = window.innerWidth < 560 })
window.addEventListener('click', () => { dropdownOpen.value = false })
```

並加入 return：`isMobile, dropdownOpen, sidebarOpen, editMode`

- [ ] **Step 3: 加入對應 CSS 到 `style.css`**

```css
/* Header */
.app-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.course-dropdown-wrap { position: relative; }

.course-dropdown-btn {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
}

.course-dropdown-menu {
  position: absolute;
  top: 110%;
  left: 0;
  min-width: 200px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.course-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
}
.course-dropdown-item:hover { background: var(--color-border); }
.course-dropdown-item.active { color: var(--color-blue); }

.course-item-actions { display: flex; gap: 4px; }
.course-item-actions button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  padding: 2px 4px;
  border-radius: 4px;
}
.course-item-actions button:hover { background: var(--color-bg); }

.course-dropdown-add, .sidebar-add {
  padding: 10px 14px;
  color: var(--color-blue);
  cursor: pointer;
  font-size: 14px;
  border-top: 1px solid var(--color-border);
}
.course-dropdown-add:hover, .sidebar-add:hover { background: var(--color-border); }

/* Mobile */
.hamburger-btn {
  background: none;
  border: none;
  color: var(--color-text);
  font-size: 22px;
  cursor: pointer;
  padding: 4px 8px;
}

.mobile-course-name {
  flex: 1;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
}

/* Sidebar */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: flex;
}

.sidebar {
  width: 260px;
  background: var(--color-surface);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-title {
  padding: 16px 14px 10px;
  font-weight: 700;
  font-size: 16px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  cursor: pointer;
  font-size: 14px;
}
.sidebar-item:hover { background: var(--color-border); }
.sidebar-item.active { color: var(--color-blue); }

.sidebar-semester {
  margin-top: auto;
  padding: 14px;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--color-muted);
}

.semester-input {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 13px;
  width: 100%;
}

/* Week badge */
.week-badge {
  font-size: 12px;
  color: var(--color-muted);
  margin-left: auto;
}

/* Edit button */
.edit-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-left: auto;
}
.edit-btn--done {
  border-color: var(--color-green);
  color: var(--color-green);
}

/* Main */
.app-main {
  padding: 14px;
  padding-bottom: 80px; /* 底部按鈕高度 */
}

.empty-state {
  text-align: center;
  color: var(--color-muted);
  margin-top: 60px;
  font-size: 15px;
}
```

- [ ] **Step 4: 瀏覽器驗證**
  - 點「＋ 新增課程」可輸入名稱新增
  - 下拉選單顯示課程、點選切換、✏️ 改名、🗑️ 刪除（含 confirm）
  - 縮小視窗到 < 560px，改為漢堡 + 側欄
  - 學期開始日可輸入，頂部顯示「第 N 週」

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 課程管理 + 頂部導覽 RWD"
```

---

## Task 3: 單元進度列表（三色進度條）

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 在 `setup()` 加入快照與進度計算邏輯**

```javascript
// 快照（依 activeCourse 載入）
const snapshot = computed(() => {
  if (!activeCourse.value) return {}
  return loadSnapshot(activeCourse.value.id)
})

// 某單元某格的顏色：'blue' | 'green' | 'gray'
function cellColor(unit, cellIndex) {
  const cellProgress = (cellIndex + 1) * 25  // 25, 50, 75, 100
  const base = snapshot.value[unit.id] ?? 0
  if (cellProgress <= base) return 'blue'
  if (cellProgress <= unit.progress) return 'green'
  return 'gray'
}

// 百分比文字顏色
function progressTextColor(unit) {
  const base = snapshot.value[unit.id] ?? 0
  if (unit.progress === 0) return 'gray'
  if (unit.progress > base) return 'green'
  return 'blue'
}

// 點擊進度格
function clickCell(unit, cellIndex) {
  if (editMode.value) return
  const target = (cellIndex + 1) * 25
  if (unit.progress === target) {
    unit.progress = Math.max(0, target - 25)
  } else {
    unit.progress = target
  }
  persist()
}
```

加入 return：`snapshot, cellColor, progressTextColor, clickCell`

- [ ] **Step 2: 在 `<main>` 內加入單元列表 HTML（一般模式）**

將 `<!-- 主體佔位 -->` 區塊替換：

```html
<main class="app-main">
  <div v-if="!activeCourse" class="empty-state">請先新增課程</div>

  <template v-else>
    <!-- 一般模式：進度列表 -->
    <div v-if="!editMode" class="unit-list">
      <div v-if="!activeCourse.units.length" class="empty-state">尚無單元，點右上角 ✏️ 新增</div>
      <div v-for="unit in activeCourse.units" :key="unit.id" class="unit-row">
        <span class="unit-name">{{ unit.name }}</span>
        <div class="unit-bar">
          <div
            v-for="(_, i) in 4" :key="i"
            class="unit-cell"
            :class="'cell--' + cellColor(unit, i)"
            @click="clickCell(unit, i)"
          ></div>
        </div>
        <span class="unit-pct" :class="'pct--' + progressTextColor(unit)">{{ unit.progress }}%</span>
      </div>
    </div>

    <!-- 編輯模式（Task 5 填入） -->
    <div v-else class="unit-list">
      <div class="empty-state">編輯模式（Task 5）</div>
    </div>

    <!-- 底部固定按鈕（Task 4 填入） -->
  </template>
</main>
```

- [ ] **Step 3: 加入單元列表 CSS**

```css
/* Unit list */
.unit-list { display: flex; flex-direction: column; gap: 10px; }

.unit-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--color-surface);
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.unit-name {
  flex: 1;
  font-size: 14px;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unit-bar {
  display: flex;
  gap: 3px;
  flex-shrink: 0;
}

.unit-cell {
  width: 28px;
  height: 14px;
  border-radius: 3px;
  cursor: pointer;
  transition: opacity 0.1s;
}
.unit-cell:hover { opacity: 0.75; }

.cell--blue { background: var(--color-blue); }
.cell--green { background: var(--color-green); }
.cell--gray { background: var(--color-gray-bar); }

.unit-pct {
  font-size: 13px;
  font-weight: 600;
  min-width: 38px;
  text-align: right;
  flex-shrink: 0;
}
.pct--gray { color: var(--color-muted); }
.pct--blue { color: var(--color-blue); }
.pct--green { color: var(--color-green); }
```

- [ ] **Step 4: 瀏覽器驗證（需先有課程與單元，用 Task 5 前先手動 localStorage 插入測試資料）**

開啟 DevTools Console 執行：

```javascript
const d = { courses: [{ id: 'c1', name: '微積分 I', units: [
  { id: 'u1', name: 'Ch1 極限', progress: 100 },
  { id: 'u2', name: 'Ch2 微分', progress: 25 },
  { id: 'u3', name: 'Ch3 積分', progress: 0 }
], weeklyLog: [] }], activeCourseId: 'c1', semesterStart: '' }
localStorage.setItem('syllabustrack_data', JSON.stringify(d))
// 設定快照：u1 = 75（之前紀錄），u2 = 0
localStorage.setItem('syllabustrack_snapshot_c1', JSON.stringify({ u1: 75, u2: 0 }))
location.reload()
```

預期：
- Ch1 極限：3 格藍 + 1 格綠（快照75%→實際100%，前3格<=75%為藍，第4格>75%且<=100%為綠）
- Ch2 微分：1 格綠 + 3 格灰（快照0%→實際25%，第1格>0%且<=25%為綠）
- Ch3 積分：4 格全灰（progress=0%）
- 點格子能即時改顏色

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 三色進度條"
```

---

## Task 4: 底部按鈕 + 記錄本週

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 加入備註輸入 overlay 與記錄本週邏輯到 `setup()`**

```javascript
const noteDialogOpen = ref(false)
const noteInput = ref('')
const noChangeMsg = ref(false)

function openRecordWeek() {
  if (!activeCourse.value) return
  const snap = snapshot.value
  const changed = activeCourse.value.units.some(u => u.progress !== (snap[u.id] ?? 0))
  if (!changed) {
    noChangeMsg.value = true
    setTimeout(() => { noChangeMsg.value = false }, 2000)
    return
  }
  noteInput.value = ''
  noteDialogOpen.value = true
}

function confirmRecordWeek() {
  const course = activeCourse.value
  const snap = snapshot.value
  const changes = course.units
    .filter(u => u.progress !== (snap[u.id] ?? 0))
    .map(u => ({ unitId: u.id, unitName: u.name, from: snap[u.id] ?? 0, to: u.progress }))

  const entry = {
    id: uuid(),
    week: calcWeekNumber(data.semesterStart, course.weeklyLog.length),
    date: todayStr(),
    note: noteInput.value.trim(),
    changes
  }
  course.weeklyLog.push(entry)
  saveSnapshot(course.id, course.units)
  persist()
  noteDialogOpen.value = false
}
```

加入 return：`noteDialogOpen, noteInput, noChangeMsg, openRecordWeek, confirmRecordWeek`

- [ ] **Step 2: 加入底部按鈕與備註 dialog HTML**

在 `</template>` 之前（緊接在 `<!-- 底部固定按鈕 -->` 後）加入：

```html
    <!-- 底部按鈕 -->
    <div class="bottom-bar" v-if="activeCourse && !editMode">
      <div v-if="noChangeMsg" class="no-change-msg">本週尚無進度變動</div>
      <button class="bottom-btn bottom-btn--primary" @click="openRecordWeek">記錄本週</button>
      <button class="bottom-btn" @click="logOpen = true">週誌</button>
    </div>

    <!-- 備註 dialog -->
    <div v-if="noteDialogOpen" class="dialog-backdrop" @click="noteDialogOpen = false">
      <div class="dialog-box" @click.stop>
        <div class="dialog-title">本週備註（可留空）</div>
        <textarea v-model="noteInput" class="dialog-textarea" placeholder="例：今天上完 Ch2，學生反應良好" rows="3" autofocus></textarea>
        <div class="dialog-actions">
          <button class="dialog-btn" @click="noteDialogOpen = false">取消</button>
          <button class="dialog-btn dialog-btn--primary" @click="confirmRecordWeek">確認記錄</button>
        </div>
      </div>
    </div>
```

並在 `setup()` 加入 `const logOpen = ref(false)`，加入 return：`logOpen`

- [ ] **Step 3: 加入 CSS**

```css
/* Bottom bar */
.bottom-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  display: flex;
  gap: 10px;
  padding: 12px 14px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  z-index: 50;
}

.bottom-btn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text);
}
.bottom-btn--primary {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: #fff;
}

.no-change-msg {
  position: absolute;
  top: -36px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-muted);
  white-space: nowrap;
}

/* Dialog */
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.dialog-box {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 20px;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-title { font-size: 15px; font-weight: 600; }

.dialog-textarea {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.dialog-actions { display: flex; gap: 8px; justify-content: flex-end; }

.dialog-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  font-size: 14px;
}
.dialog-btn--primary {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: #fff;
}
```

- [ ] **Step 4: 瀏覽器驗證**
  - 點「記錄本週」，若無變動出現「本週尚無進度變動」提示
  - 有變動時出現備註輸入框，確認後週誌條目建立（DevTools 看 localStorage）
  - 確認後快照更新，綠格轉藍

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 記錄本週 + 備註輸入"
```

---

## Task 5: 週誌 Overlay

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 加入週誌邏輯到 `setup()`**

```javascript
const logIndex = ref(0)  // 目前顯示的週誌 index（從最新開始）

const sortedLog = computed(() => {
  if (!activeCourse.value) return []
  return [...activeCourse.value.weeklyLog].reverse()  // 最新在前
})

const currentLogEntry = computed(() => sortedLog.value[logIndex.value] || null)

function openLog() {
  logIndex.value = 0
  logOpen.value = true
}

function logPrev() { if (logIndex.value < sortedLog.value.length - 1) logIndex.value++ }
function logNext() { if (logIndex.value > 0) logIndex.value-- }

// 週誌進度條格顏色
function logCellColor(change, cellIndex) {
  const cellProgress = (cellIndex + 1) * 25
  if (cellProgress <= change.from) return 'blue'
  if (cellProgress <= change.to) return 'green'
  return 'gray'
}
```

加入 return：`logOpen, logIndex, sortedLog, currentLogEntry, openLog, logPrev, logNext, logCellColor`

並將 `@click="logOpen = true"` 改為 `@click="openLog()"`

- [ ] **Step 2: 加入週誌 overlay HTML（放在 dialog 之後）**

```html
    <!-- 週誌 Overlay -->
    <div v-if="logOpen" class="log-backdrop" @click="logOpen = false">
      <div class="log-panel" @click.stop>
        <!-- 標題 -->
        <div class="log-header">
          <span class="log-title">週誌 — {{ activeCourse.name }}</span>
          <button class="log-close" @click="logOpen = false">✕</button>
        </div>

        <!-- 週次切換列 -->
        <div class="log-week-nav" v-if="sortedLog.length">
          <button class="log-nav-btn" @click="logPrev" :disabled="logIndex >= sortedLog.length - 1">←</button>
          <span class="log-week-label">第 {{ currentLogEntry.week }} 週</span>
          <button class="log-nav-btn" @click="logNext" :disabled="logIndex <= 0">→</button>
        </div>

        <!-- 內容 -->
        <div class="log-body">
          <div v-if="!sortedLog.length" class="empty-state">尚無週誌紀錄</div>
          <template v-else-if="currentLogEntry">
            <div class="log-meta">{{ formatDate(currentLogEntry.date) }}</div>
            <div v-if="currentLogEntry.note" class="log-note">{{ currentLogEntry.note }}</div>
            <div class="log-changes">
              <div v-for="ch in currentLogEntry.changes" :key="ch.unitId" class="log-change-row">
                <div class="log-change-header">
                  <span class="log-change-name">{{ ch.unitName }}</span>
                  <span class="log-change-pct">{{ ch.from }}% → {{ ch.to }}%</span>
                </div>
                <div class="log-change-bar">
                  <div
                    v-for="(_, i) in 4" :key="i"
                    class="unit-cell"
                    :class="'cell--' + logCellColor(ch, i)"
                    style="cursor:default"
                  ></div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
```

- [ ] **Step 3: 加入週誌 CSS**

```css
/* Log overlay */
.log-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
}

.log-panel {
  width: 100%;
  height: 70vh;
  background: var(--color-surface);
  border-radius: 16px 16px 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
}

.log-title { font-size: 15px; font-weight: 700; }

.log-close {
  background: none;
  border: none;
  color: var(--color-muted);
  font-size: 18px;
  cursor: pointer;
}

.log-week-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 10px;
  border-bottom: 1px solid var(--color-border);
}

.log-nav-btn {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 4px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}
.log-nav-btn:disabled { opacity: 0.3; cursor: default; }

.log-week-label { font-size: 15px; font-weight: 600; min-width: 80px; text-align: center; }

.log-body { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 12px; }

.log-meta { font-size: 12px; color: var(--color-muted); }

.log-note {
  font-size: 13px;
  color: var(--color-muted);
  background: var(--color-bg);
  padding: 8px 10px;
  border-radius: 6px;
  white-space: pre-wrap;
}

.log-changes { display: flex; flex-direction: column; gap: 10px; }

.log-change-row {
  background: var(--color-bg);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.log-change-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-change-name { font-size: 14px; }
.log-change-pct { font-size: 13px; color: var(--color-muted); }

.log-change-bar { display: flex; gap: 3px; }
```

- [ ] **Step 4: 瀏覽器驗證**
  - 點「週誌」從底部滑出，顯示最新週
  - 左右箭頭切換週，到邊界時按鈕 disabled
  - 備註顯示在日期下方
  - 每個有變動的單元顯示藍/綠/灰進度條

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 週誌 overlay"
```

---

## Task 6: 編輯課程模式（單元增刪改排序）

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 加入單元管理邏輯到 `setup()`**

```javascript
const editingUnitId = ref(null)
const editingUnitName = ref('')
const dragSrcIndex = ref(null)

function addUnit() {
  if (!activeCourse.value) return
  const u = { id: uuid(), name: '新單元', progress: 0 }
  activeCourse.value.units.push(u)
  persist()
  nextTick(() => {
    editingUnitId.value = u.id
    editingUnitName.value = u.name
  })
}

function startRename(unit) {
  editingUnitId.value = unit.id
  editingUnitName.value = unit.name
}

function commitRename(unit) {
  if (editingUnitName.value.trim()) {
    unit.name = editingUnitName.value.trim()
    persist()
  }
  editingUnitId.value = null
}

function deleteUnit(unit) {
  if (!confirm(`確定刪除「${unit.name}」？`)) return
  const idx = activeCourse.value.units.findIndex(u => u.id === unit.id)
  activeCourse.value.units.splice(idx, 1)
  persist()
}

function onDragStart(index) { dragSrcIndex.value = index }

function onDragOver(e, index) {
  e.preventDefault()
  if (dragSrcIndex.value === null || dragSrcIndex.value === index) return
  const units = activeCourse.value.units
  const moved = units.splice(dragSrcIndex.value, 1)[0]
  units.splice(index, 0, moved)
  dragSrcIndex.value = index
}

function onDragEnd() { dragSrcIndex.value = null; persist() }
```

加入 return：`editingUnitId, editingUnitName, addUnit, startRename, commitRename, deleteUnit, onDragStart, onDragOver, onDragEnd`

- [ ] **Step 2: 將編輯模式的 `<div v-else>` 替換為完整 HTML**

```html
    <!-- 編輯模式 -->
    <div v-else class="unit-list">
      <div
        v-for="(unit, idx) in activeCourse.units"
        :key="unit.id"
        class="unit-row unit-row--edit"
        draggable="true"
        @dragstart="onDragStart(idx)"
        @dragover="onDragOver($event, idx)"
        @dragend="onDragEnd"
      >
        <span class="drag-handle">☰</span>
        <template v-if="editingUnitId === unit.id">
          <input
            class="unit-name-input"
            v-model="editingUnitName"
            @blur="commitRename(unit)"
            @keyup.enter="commitRename(unit)"
            @keyup.escape="editingUnitId = null"
            autofocus
          >
        </template>
        <span v-else class="unit-name unit-name--edit" @click="startRename(unit)">{{ unit.name }}</span>
        <button class="unit-delete-btn" @click="deleteUnit(unit)">✕</button>
      </div>
      <button class="add-unit-btn" @click="addUnit">＋ 新增單元</button>
    </div>
```

- [ ] **Step 3: 加入編輯模式 CSS**

```css
.unit-row--edit { cursor: default; }

.drag-handle {
  color: var(--color-muted);
  cursor: grab;
  font-size: 16px;
  flex-shrink: 0;
}

.unit-name--edit {
  flex: 1;
  cursor: text;
  padding: 2px 4px;
  border-radius: 4px;
}
.unit-name--edit:hover { background: var(--color-border); }

.unit-name-input {
  flex: 1;
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-blue);
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
  font-family: inherit;
}

.unit-delete-btn {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  font-size: 15px;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}
.unit-delete-btn:hover { color: #ef4444; background: var(--color-bg); }

.add-unit-btn {
  width: 100%;
  padding: 12px;
  border: 1px dashed var(--color-border);
  border-radius: 8px;
  background: none;
  color: var(--color-blue);
  cursor: pointer;
  font-size: 14px;
  margin-top: 4px;
}
.add-unit-btn:hover { background: var(--color-surface); }
```

- [ ] **Step 4: 瀏覽器驗證**
  - 點 ✏️ 進入編輯模式，頂部出現「完成編輯」按鈕
  - 可點單元名稱 inline 改名（enter/blur 確認，esc 取消）
  - ✕ 刪除有 confirm
  - ☰ 拖曳排序（桌機）
  - ＋ 新增單元後自動 focus 到輸入框
  - 點「完成編輯」回一般模式，進度條可點

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 編輯課程模式（單元增刪改排序）"
```

---

## Task 7: 細節收尾 + 學期週次設定

**Files:**
- Modify: `SyllabusTrack/index.html`
- Modify: `SyllabusTrack/style.css`

- [ ] **Step 1: 確認學期開始日已在 Task 2 側欄實作，桌機在下拉選單沒有此設定 — 補到桌機版**

在下拉選單 `.course-dropdown-menu` 最底部（`course-dropdown-add` 之後）加入：

```html
<div class="dropdown-semester" @click.stop>
  <label>學期開始日</label>
  <input type="date" v-model="semesterStart" class="semester-input">
</div>
```

```css
.dropdown-semester {
  padding: 10px 14px;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--color-muted);
}
```

- [ ] **Step 2: 手機版底部按鈕在編輯模式下隱藏（已由 `v-if="!editMode"` 控制，確認正確）**

確認 `class="bottom-bar"` 的元素有 `v-if="activeCourse && !editMode"`，若無則加上。

- [ ] **Step 3: 加入 `<title>` 動態顯示目前課程名**

在 Vue 的 `setup()` 加入（onMounted 之內或之後）：

將 Task 1 `index.html` 頂部的 import 改為：

```javascript
import { createApp, ref, reactive, computed, onMounted, nextTick, watch } from '../framework/vue.esm-browser.js'
```

然後在 `setup()` 內加入：

```javascript
watch(activeCourse, c => {
  document.title = c ? `${c.name} — SyllabusTrack` : 'SyllabusTrack'
}, { immediate: true })
```

- [ ] **Step 4: 整體 RWD 最終驗證**

| 場景 | 預期 |
|------|------|
| 手機 < 560px，無課程 | 漢堡 + 「選擇課程」，主體「請先新增課程」 |
| 手機，新增課程 + 單元 | 單元列表正常，底部兩按鈕可點 |
| 手機，記錄本週有變動 | 彈出備註框，確認後週誌新增一筆 |
| 手機，開啟週誌 | 底部滑出，左右切換週，備註與進度條正確顯示 |
| 手機，編輯模式 | 增刪改名 ok，底部按鈕隱藏 |
| 桌機 ≥ 560px | 下拉選單，功能同上 |

- [ ] **Step 5: Commit**

```bash
git add SyllabusTrack/index.html SyllabusTrack/style.css
git commit -m "feat(SyllabusTrack): 細節收尾 + 學期週次設定"
```

---

## Task 8: 加入 `.gitignore` 條目

**Files:**
- Modify: `d:\VibePage\.gitignore`（若存在）或新建

- [ ] **Step 1: 確認 `.gitignore` 包含 `.superpowers/`**

```bash
# 若 .gitignore 不存在
echo ".superpowers/" >> .gitignore
# 若已存在則確認是否已有此行，沒有就加上
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore .superpowers brainstorm files"
```
