"""
extract_class.py
從「班級課表.pdf」解析每個班級的課表，輸出 data/schedule_class.json

執行方式（從 Course/ 目錄下）：
    python data/extract_class.py [pdf_path]
預設 pdf_path: data/班級課表.pdf
"""
import pdfplumber, json, re, unicodedata, sys, warnings
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else 'data/班級課表.pdf'
OUT_PATH = 'data/schedule_class.json'

# row index → period（班級課表固定格式）
ROW_PERIOD = {0:'1', 1:'2', 2:'3', 3:'4', 5:'5', 6:'6', 7:'7', 8:'8',
              9:'9', 10:'10', 11:'A', 12:'B', 13:'C', 14:'D'}
# row 4 = 中午, rows 9/10 = skip
DAY_COL = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}
DAY_HEADERS = {'星期一','星期二','星期三','星期四','星期五','星期六','星期日'}
ROOM_RE = re.compile(r'^[A-Za-z]{1,3}\d{2,4}$')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

def is_room(s):
    return bool(ROOM_RE.match(s.strip()))

def is_teacher(s):
    s = s.strip().rstrip('.')
    return bool(re.match(r'^[\u2e80-\u2fff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]{2,5}$', s))

def clean_teacher(s):
    return s.strip().rstrip('.')

def clean_line(s):
    s = re.sub(r'院共同時段?', '', s).strip()
    return s

def join_cjk(lines):
    return ''.join(lines)

def parse_cell(text):
    if not text or not text.strip():
        return None
    raw = nfc(text.strip())
    if re.fullmatch(r'院共同時段?', raw):
        return None

    lines = [clean_line(nfc(x.strip())) for x in raw.split('\n')]
    lines = [l for l in lines if l and l != '段' and l not in DAY_HEADERS]
    if not lines:
        return None

    room = ''
    teacher = ''

    if lines and is_room(lines[-1]):
        room = lines.pop()

    if lines and is_teacher(clean_teacher(lines[-1])):
        teacher = clean_teacher(lines.pop())

    course = join_cjk(lines)
    if not course:
        return None
    return {'course': course, 'teacher': teacher, 'room': room}

results = []
log = []

with pdfplumber.open(PDF_PATH) as pdf:
    for pi, page in enumerate(pdf.pages):
        try:
            text = nfc(page.extract_text() or '')
        except Exception:
            text = ''

        m = re.search(r'班級[:：](.+?)(?:\s+\()', text)
        class_name = nfc(m.group(1).strip()) if m else f'page{pi}'

        try:
            tables = page.extract_tables()
        except Exception:
            tables = []
        if not tables:
            log.append(f'{class_name}: 0')
            continue
        table = tables[0]

        entries = []
        for row_i, row in enumerate(table):
            if row_i not in ROW_PERIOD:
                continue
            period = ROW_PERIOD[row_i]
            for col_i, day in DAY_COL.items():
                if col_i >= len(row):
                    continue
                cell = nfc(str(row[col_i]) if row[col_i] else '')
                if not cell.strip() or cell.strip() == 'None':
                    continue
                parsed = parse_cell(cell)
                if parsed:
                    entries.append({
                        'teacher': parsed['teacher'],
                        'day': day,
                        'period': period,
                        'course': parsed['course'],
                        'room': parsed['room'],
                        'class': class_name,
                    })

        log.append(f'{class_name}: {len(entries)}')
        results.extend(entries)

log.append(f'TOTAL: {len(results)}')

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n'.join(log))
print(f'\n✓ 輸出 {OUT_PATH}（{len(results)} 筆）')
