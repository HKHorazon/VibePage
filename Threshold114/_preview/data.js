// 必修課程資料 — 5 種排版範例共用
window.SEMESTERS = [
  {
    id: '1a', label: '一上', year: '大一', courses: [
      { name: 'ACGE 概論', credits: 2, hours: 2, type: 'required' },
      { name: '遊戲企劃', credits: 2, hours: 2, type: 'required' },
      { name: '基礎攝影與剪輯', credits: 3, hours: 3, type: 'required' },
      { name: '設計概論', credits: 3, hours: 3, type: 'required' },
      { name: '原畫設計', credits: 3, hours: 3, type: 'required' },
      { name: '中文閱讀與書寫(一)', credits: 2, hours: 2, type: 'general' },
      { name: '英文(一)', credits: 2, hours: 2, type: 'general' },
      { name: '人文精神(一)', credits: 2, hours: 2, type: 'general' },
      { name: '服務學習(一)', credits: 0, hours: 1, type: 'general' }
    ]
  },
  {
    id: '1b', label: '一下', year: '大一', courses: [
      { name: '2D 動畫', credits: 3, hours: 3, type: 'required' },
      { name: '產品行銷', credits: 2, hours: 2, type: 'required' },
      { name: '基礎 AI 應用', credits: 2, hours: 2, type: 'required' },
      { name: '中文閱讀與書寫(二)', credits: 2, hours: 2, type: 'general' },
      { name: '英文(二)', credits: 2, hours: 2, type: 'general' },
      { name: '體育', credits: 2, hours: 2, type: 'general' },
      { name: '應用程式設計', credits: 2, hours: 2, type: 'general' }
    ]
  },
  {
    id: '2a', label: '二上', year: '大二', courses: [
      { name: '提案與簡報技巧', credits: 2, hours: 3, type: 'required' },
      { name: '劇本寫作與腳本設計', credits: 2, hours: 2, type: 'required' },
      { name: '基礎遊戲引擎應用', credits: 3, hours: 3, type: 'required' },
      { name: '歷史與文明', credits: 2, hours: 2, type: 'general' },
      { name: '人文精神(二)', credits: 2, hours: 2, type: 'general' },
      { name: '服務學習(二)', credits: 0, hours: 1, type: 'general' }
    ]
  },
  {
    id: '2b', label: '二下', year: '大二', courses: [
      { name: '短影片製作', credits: 3, hours: 3, type: 'required' },
      { name: '互動媒體製作', credits: 3, hours: 3, type: 'required' },
      { name: '數位音訊控制', credits: 2, hours: 2, type: 'required' },
      { name: '職場專業英文簡報', credits: 2, hours: 2, type: 'general' },
      { name: '創意概論', credits: 2, hours: 2, type: 'general' }
    ]
  },
  {
    id: '3a', label: '三上', year: '大三', courses: [
      { name: '消費者心理學', credits: 2, hours: 2, type: 'required' },
      { name: '專題製作(一)', credits: 2, hours: 3, type: 'required' },
      { name: '多媒體商業模式', credits: 2, hours: 2, type: 'required' },
      { name: '創新思維與應用', credits: 2, hours: 2, type: 'general' },
      { name: '社會科學類(選修)', credits: 2, hours: 2, type: 'general' }
    ]
  },
  {
    id: '3b', label: '三下', year: '大三', courses: [
      { name: '專案管理', credits: 3, hours: 3, type: 'required' },
      { name: '自媒體經營與管理', credits: 2, hours: 2, type: 'required' },
      { name: '專題製作(二)', credits: 2, hours: 3, type: 'required' },
      { name: '民主與法治', credits: 2, hours: 2, type: 'general' },
      { name: '人文藝術類(選修)', credits: 2, hours: 2, type: 'general' }
    ]
  },
  {
    id: '4a', label: '四上', year: '大四', courses: [
      { name: '畢業專題', credits: 2, hours: 3, type: 'required' },
      { name: '專業實習', credits: 4, hours: 4, type: 'required' },
      { name: '展演設計', credits: 2, hours: 2, type: 'required' }
    ]
  },
  {
    id: '4b', label: '四下', year: '大四', courses: [
      { name: '畢業展演實務', credits: 3, hours: 3, type: 'required' }
    ]
  }
];

window.sumBy = function (courses, type) {
  return courses.filter(c => !type || c.type === type).reduce((s, c) => s + c.credits, 0);
};

window.DOCS = [
  { label: '系上課程總表與地圖', url: 'https://mgda.hk.edu.tw/%e8%aa%b2%e7%a8%8b%e7%b8%bd%e8%a1%a8%e8%88%87%e5%9c%b0%e5%9c%96/' },
  { label: '日間部 U114 科目總表（PDF）', url: 'https://mgda.hk.edu.tw/wp-content/uploads/2025/08/%E6%97%A5%E9%96%93%E9%83%A8U114%E7%A7%91%E7%9B%AE%E7%B8%BD%E8%A1%A8.pdf' },
  { label: '114 學年度四年制日間部課程架構地圖（PDF）', url: 'https://mgda.hk.edu.tw/wp-content/uploads/2025/08/114%E5%AD%B8%E5%B9%B4%E5%BA%A6%E5%9B%9B%E5%B9%B4%E5%88%B6%E6%97%A5%E9%96%93%E9%83%A8%E8%AA%B2%E7%A8%8B%E6%9E%B6%E6%A7%8B%E5%9C%B0%E5%9C%96.pdf' },
  { label: '系所問題 QA', url: 'https://mgda.hk.edu.tw/%e7%b3%bb%e6%89%80%e5%95%8f%e9%a1%8cqa/' }
];

window.NOTES = [
  '選修課與體育課保證不和必修衝堂（通識選修可能衝，請自行確認）',
  '必修課程不得以其他課程替代 or 抵免',
  '轉系、轉學生請洽系辦確認抵免規定'
];
