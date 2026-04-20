"""
extract_teacher.py
從「多遊系教師課表.pdf」解析每位老師的課表，輸出 data/schedule_teacher.json

執行方式（從 Course/ 目錄下）：
    python data/extract_teacher.py [pdf_path]
預設 pdf_path: data/1142多遊系教師課表.pdf
"""
import pdfplumber, json, re, unicodedata, sys, warnings
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else 'data/1142多遊系教師課表.pdf'
OUT_PATH = 'data/schedule_teacher.json'

PERIOD_MAP = {'1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8',
              'A':'A','B':'B','C':'C','D':'D'}
DAY_MAP = {'星期一':'一','星期二':'二','星期三':'三','星期四':'四','星期五':'五',
           '一':'一','二':'二','三':'三','四':'四','五':'五',
           # PDF 常用 CJK 部首補充字元（⼀=U+2F00，⼆=U+2F01）
           '\u661f\u671f\u2f00':'一','\u661f\u671f\u2f01':'二',
           '\u2f00':'一','\u2f01':'二'}
SKIP_PERIODS = {'中午','9','10','第9','第10'}
ROOM_RE = re.compile(r'[A-Z]{1,5}\d{3,4}')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

def join_lines(lines):
    """合併多行文字：中文接中文不加空格，英數接英數加空格"""
    result = ''
    for line in lines:
        if not line:
            continue
        if result:
            last = result[-1]
            first = line[0]
            is_cjk = lambda c: '\u2e80' <= c <= '\u9fff' or '\uf900' <= c <= '\ufaff'
            if is_cjk(last) or is_cjk(first):
                result += line
            else:
                result += ' ' + line
        else:
            result = line
    return result

def parse_cell(raw):
    """解析教師課表格子：課程 + 教室代碼 + 班級"""
    raw = unicodedata.normalize('NFKC', raw.strip())
    if not raw or 'Office Hours' in raw or 'office hours' in raw.lower():
        return None
    lines = [nfc(x.strip()) for x in raw.split('\n') if x.strip()]
    if not lines:
        return None

    text = join_lines(lines)
    m = ROOM_RE.search(text)
    if m:
        course = text[:m.start()].strip()
        room = m.group()
        class_name = text[m.end():].strip()
    else:
        # 嘗試找日四技 / 夜四技 作為班級起始點（含 CJK 部首變體）
        m2 = re.search(r'[\u65e5\u2f0a\u591c\u2f46]四技', text)
        if m2:
            course = text[:m2.start()].strip()
            room = ''
            class_name = text[m2.start():].strip()
        else:
            course = text
            room = ''
            class_name = ''

    if not course:
        return None
    return {'course': course, 'room': room, 'class': class_name}

def parse_period_label(label):
    """從節次標籤取出期號：第3 → 3，第A → A，中午 → None"""
    if not label:
        return None
    label = nfc(label.strip())
    if label in SKIP_PERIODS:
        return None
    m = re.match(r'第?([1-8A-D])', label)
    if m:
        p = m.group(1)
        return PERIOD_MAP.get(p)
    return None

results = []
log = []

with pdfplumber.open(PDF_PATH) as pdf:
    for pi, page in enumerate(pdf.pages):
        try:
            text = nfc(page.extract_text() or '')
        except Exception:
            text = ''

        # 從頁面文字取老師姓名：找「授課教師：」下一行
        teacher_name = ''
        lines_text = [nfc(l.strip()) for l in text.split('\n') if nfc(l.strip())]
        for li, line in enumerate(lines_text):
            if '授課教師' in line:
                # 姓名可能在同行「授課教師：楊國隆」或下一行「楊國隆」
                after = re.sub(r'.*授課教師[：:]?\s*', '', line).strip()
                CJK = r'[\u2e80-\u2fff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]'
                if after and re.fullmatch(CJK + r'{2,5}', after):
                    teacher_name = after
                elif li + 1 < len(lines_text):
                    nxt = lines_text[li + 1]
                    if re.fullmatch(CJK + r'{2,5}', nxt):
                        teacher_name = nxt
                break

        if not teacher_name:
            log.append(f'page{pi}: 無法識別老師名稱，略過')
            continue

        try:
            tables = page.extract_tables()
        except Exception:
            tables = []
        if not tables:
            log.append(f'{teacher_name}: 無表格')
            continue

        table = tables[0]
        entries = []

        # 找表頭列（含星期）
        header_row = None
        day_cols = {}
        for ri, row in enumerate(table):
            for ci, cell in enumerate(row):
                val = nfc(str(cell or '').strip())
                if val in DAY_MAP:
                    day_cols[ci] = DAY_MAP[val]
            if day_cols:
                header_row = ri
                break

        # 補齊未偵測到的欄位（固定格式：col2-6 = 一-五）
        DEFAULT_DAY_COLS = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}
        for ci, day in DEFAULT_DAY_COLS.items():
            if day not in day_cols.values():
                day_cols[ci] = day

        for ri, row in enumerate(table):
            if header_row is not None and ri == header_row:
                continue
            # 取節次（第 0 欄）
            period_cell = nfc(str(row[0] or '').strip()) if row else ''
            period = parse_period_label(period_cell)
            if not period:
                continue

            for ci, day in day_cols.items():
                if ci >= len(row):
                    continue
                raw = nfc(str(row[ci] or ''))
                if not raw.strip() or raw.strip() == 'None':
                    continue
                parsed = parse_cell(raw)
                if parsed:
                    entries.append({
                        'teacher': teacher_name,
                        'day': day,
                        'period': period,
                        'course': parsed['course'],
                        'room': parsed['room'],
                        'class': parsed['class'],
                    })

        log.append(f'{teacher_name}: {len(entries)}')
        results.extend(entries)

log.append(f'TOTAL: {len(results)}')

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n'.join(log))
print(f'\n✓ 輸出 {OUT_PATH}（{len(results)} 筆）')
