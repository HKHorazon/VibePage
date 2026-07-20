import { createApp, reactive, computed, onMounted, onUnmounted } from '../framework/vue.esm-browser.js'

const padCode = (i) => String(i + 1).padStart(2, '0')

const splitName = (name) => {
  const m = String(name).match(/^(.*?)\s*[（(]([^（）()]+)[）)]\s*$/)
  if (m) return { mainName: m[1].trim(), tag: m[2].trim() }
  return { mainName: name, tag: '' }
}

const DocLayout = {
  props: {
    currentFile: { type: String, default: '' },
    dataPath: { type: String, default: './Data/articles.json' },
    indexPath: { type: String, default: './index.html' },
    filePrefix: { type: String, default: './' },
  },
  setup(props) {
    const state = reactive({
      rawCategories: [],
      loading: true,
      error: false,
      sidebarOpen: false,
      collapsed: {},
    })

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

    const toggleCategory = (name) => {
      state.collapsed[name] = !state.collapsed[name]
    }

    const toggleSidebar = () => {
      state.sidebarOpen = !state.sidebarOpen
    }

    const closeSidebar = () => {
      state.sidebarOpen = false
    }

    const resolveFile = (file) => props.filePrefix + file

    const isActive = (file) => file === props.currentFile

    const handleKey = (e) => {
      if (e.key === 'Escape') closeSidebar()
    }

    onMounted(async () => {
      window.addEventListener('keydown', handleKey)
      try {
        const res = await fetch(props.dataPath)
        if (!res.ok) throw new Error()
        const data = await res.json()
        if (Array.isArray(data)) {
          state.rawCategories = [{ code: '01', name: '未分類', articles: data }]
        } else {
          state.rawCategories = data.categories || []
        }
      } catch {
        state.error = true
      } finally {
        state.loading = false
      }
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKey)
    })

    return {
      state,
      categories,
      activeIndex,
      toggleCategory,
      toggleSidebar,
      closeSidebar,
      resolveFile,
      isActive,
    }
  },
  template: `
    <div class="layout-shell" :class="{ 'sidebar-open': state.sidebarOpen }">
      <div class="bg-fx" aria-hidden="true">
        <div class="bg-grid"></div>
        <div class="bg-scanlines"></div>
      </div>
      <div class="j-petals" aria-hidden="true">
        <span class="j-petal">✿</span>
        <span class="j-petal">❀</span>
        <span class="j-petal">✿</span>
        <span class="j-petal">❁</span>
        <span class="j-petal">✿</span>
        <span class="j-petal">❀</span>
        <span class="j-petal">✿</span>
        <span class="j-petal">❁</span>
      </div>

      <header class="site-header">
        <div class="header-inner">
          <button
            type="button"
            class="hamburger"
            :class="{ active: state.sidebarOpen }"
            @click="toggleSidebar"
            aria-label="切換目錄"
          >
            <span></span><span></span><span></span>
          </button>
          <a :href="indexPath" class="site-title">
            <span class="brand-dark">多遊系日本amps短期研習</span>
            <span class="brand-rainbow"><span class="brand-rainbow-sep">❀</span> 2026</span>
          </a>
          <span class="header-meta" v-if="activeIndex">
            <span class="header-meta-dot"></span>
            <span class="header-meta-text">{{ activeIndex }}</span>
          </span>
        </div>
      </header>

      <div class="sidebar-backdrop" @click="closeSidebar"></div>

      <div class="layout-body">
        <aside class="sidebar">
          <a :href="indexPath" class="sidebar-heading" @click="closeSidebar">
            <span class="sidebar-heading-prefix">✿</span>
            <span class="sidebar-heading-text">目錄</span>
            <span class="sidebar-heading-home" aria-hidden="true">⌂</span>
          </a>

          <div v-if="state.loading" class="state-msg">✿ 載入中…</div>
          <div v-else-if="state.error" class="state-msg state-msg--error">✿ 無法載入</div>

          <nav v-else class="sidebar-nav">
            <div v-for="cat in categories" :key="cat.name" class="sidebar-category">
              <button
                type="button"
                class="sidebar-category-btn"
                :class="{ collapsed: state.collapsed[cat.name] }"
                @click="toggleCategory(cat.name)"
              >
                <span class="sidebar-caret">▾</span>
                <span class="sidebar-category-code">{{ cat.code }}</span>
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
                  <a
                    :href="resolveFile(a.file)"
                    :class="{ active: isActive(a.file) }"
                    @click="closeSidebar"
                  >
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
