import { createApp, reactive, computed, ref, onMounted, onUnmounted } from '../framework/vue.esm-browser.js'

const padCode = (i) => String(i + 1).padStart(2, '0')

const splitName = (name) => {
  const m = String(name).match(/^(.*?)\s*[（(]([^（）()]+)[）)]\s*$/)
  if (m) return { mainName: m[1].trim(), tag: m[2].trim() }
  return { mainName: name, tag: '' }
}

const DocLayout = {
  props: {
    currentFile: { type: String, default: '' },
    dataPath:    { type: String, default: './Data/articles.json' },
    indexPath:   { type: String, default: './index.html' },
    filePrefix:  { type: String, default: './' },
  },
  setup(props) {
    const state = reactive({
      rawCategories: [],
      loading: true,
      error: false,
      sidebarOpen: false,
      collapsed: {},
    })

    const theme = ref(localStorage.getItem('threshold114-theme') || 'light')

    const applyTheme = (t) => {
      document.body.dataset.theme = t
      localStorage.setItem('threshold114-theme', t)
    }

    const toggleTheme = () => {
      theme.value = theme.value === 'light' ? 'dark' : 'light'
      applyTheme(theme.value)
    }

    const categories = computed(() =>
      state.rawCategories.map((cat, i) => {
        const rawName = cat.name || '未分類'
        const { mainName, tag } = splitName(rawName)
        return {
          code: cat.code || padCode(i),
          name: rawName,
          mainName,
          tag,
          articles: (cat.articles || []).map((a, j) => ({
            ...a,
            index: `${cat.code || padCode(i)}.${padCode(j)}`,
          })),
        }
      })
    )

    const activeIndex = computed(() => {
      for (const cat of categories.value) {
        const hit = cat.articles.find((a) => a.file === props.currentFile)
        if (hit) return hit.index
      }
      return ''
    })

    // 跨類別攤平成單一序列，供上一頁／下一頁使用（不循環）
    const flatArticles = computed(() => categories.value.flatMap((cat) => cat.articles))
    const currentPos   = computed(() => flatArticles.value.findIndex((a) => a.file === props.currentFile))
    const prevArticle  = computed(() => currentPos.value > 0 ? flatArticles.value[currentPos.value - 1] : null)
    const nextArticle  = computed(() => {
      const i = currentPos.value
      return i >= 0 && i < flatArticles.value.length - 1 ? flatArticles.value[i + 1] : null
    })

    const toggleCategory = (name) => { state.collapsed[name] = !state.collapsed[name] }
    const toggleSidebar  = () => { state.sidebarOpen = !state.sidebarOpen }
    const closeSidebar   = () => { state.sidebarOpen = false }
    const resolveFile    = (file) => props.filePrefix + file
    const isActive       = (file) => file === props.currentFile

    const handleKey = (e) => { if (e.key === 'Escape') closeSidebar() }

    onMounted(async () => {
      applyTheme(theme.value)
      window.addEventListener('keydown', handleKey)
      try {
        const res = await fetch(props.dataPath)
        if (!res.ok) throw new Error()
        const data = await res.json()
        state.rawCategories = Array.isArray(data)
          ? [{ code: '01', name: '未分類', articles: data }]
          : (data.categories || [])
      } catch {
        state.error = true
      } finally {
        state.loading = false
      }
    })

    onUnmounted(() => { window.removeEventListener('keydown', handleKey) })

    return {
      state, categories, activeIndex, theme,
      toggleTheme, toggleCategory, toggleSidebar, closeSidebar,
      resolveFile, isActive, prevArticle, nextArticle,
    }
  },
  template: `
    <div class="layout-shell" :class="{ 'sidebar-open': state.sidebarOpen }">
      <div class="bg-fx" aria-hidden="true"><div class="bg-grid"></div></div>

      <header class="site-header">
        <div class="header-inner">
          <button type="button" class="hamburger" :class="{ active: state.sidebarOpen }"
            @click="toggleSidebar" aria-label="切換目錄">
            <span></span><span></span><span></span>
          </button>
          <a :href="indexPath" class="site-title">
            <span class="brand-dark">多遊系</span>
            <span class="brand-rainbow"><span class="brand-rainbow-sep">//</span> 114 畢業門檻</span>
          </a>
          <div class="header-right">
            <span class="header-meta" v-if="activeIndex">
              <span class="header-meta-dot"></span>
              <span class="header-meta-text">{{ activeIndex }}</span>
            </span>
            <button type="button" class="theme-toggle" @click="toggleTheme"
              :aria-label="theme === 'dark' ? '切換白天模式' : '切換黑夜模式'">
              <span class="theme-icon">{{ theme === 'dark' ? '☀' : '☽' }}</span>
            </button>
          </div>
        </div>
      </header>

      <div class="sidebar-backdrop" @click="closeSidebar"></div>

      <div class="layout-body">
        <aside class="sidebar">
          <a :href="indexPath" class="sidebar-heading" @click="closeSidebar">
            <span class="sidebar-heading-prefix">&gt;_</span>
            <span class="sidebar-heading-text">THRESHOLD.INDEX</span>
            <span class="sidebar-heading-home" aria-hidden="true">⌂</span>
          </a>

          <div v-if="state.loading" class="state-msg">// 載入中…</div>
          <div v-else-if="state.error" class="state-msg state-msg--error">// 無法載入</div>

          <nav v-else class="sidebar-nav">
            <div v-for="cat in categories" :key="cat.name" class="sidebar-category">
              <button type="button" class="sidebar-category-btn"
                :class="{ collapsed: state.collapsed[cat.name] }"
                @click="toggleCategory(cat.name)">
                <span class="sidebar-caret">▾</span>
                <span class="sidebar-category-code">CAT_{{ cat.code }}</span>
                <span class="sidebar-category-name">
                  <span class="sidebar-category-main">{{ cat.mainName }}</span>
                  <span v-if="cat.tag" class="sidebar-category-tag">{{ cat.tag }}</span>
                </span>
                <span class="sidebar-category-count">{{ cat.articles.length }}</span>
              </button>
              <ul v-show="!state.collapsed[cat.name]" class="sidebar-articles">
                <li v-if="cat.articles.length === 0" class="sidebar-empty">
                  <span class="sidebar-empty-dash">—</span> 敬請期待
                </li>
                <li v-for="a in cat.articles" :key="a.file">
                  <a :href="resolveFile(a.file)" :class="{ active: isActive(a.file) }"
                    @click="closeSidebar">
                    <span class="article-link-index">{{ a.index }}</span>
                    <span class="article-link-title">{{ a.title }}</span>
                  </a>
                </li>
              </ul>
            </div>
          </nav>
        </aside>

        <main class="layout-main">
          <div class="content-container">
            <slot></slot>

            <nav class="page-nav" v-if="prevArticle || nextArticle">
              <a v-if="prevArticle" :href="resolveFile(prevArticle.file)" class="page-nav-link page-nav-prev">
                <span class="page-nav-dir">← PREV</span>
                <span class="page-nav-title">{{ prevArticle.index }} {{ prevArticle.title }}</span>
              </a>
              <span v-else class="page-nav-spacer"></span>

              <a v-if="nextArticle" :href="resolveFile(nextArticle.file)" class="page-nav-link page-nav-next">
                <span class="page-nav-dir">NEXT →</span>
                <span class="page-nav-title">{{ nextArticle.index }} {{ nextArticle.title }}</span>
              </a>
              <span v-else class="page-nav-spacer"></span>
            </nav>
          </div>
        </main>
      </div>
    </div>
  `,
}

export { DocLayout }

export function mountDocLayout(selector) {
  createApp({ components: { DocLayout } }).mount(selector)
}
