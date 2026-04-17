import pdfplumber, json, re, unicodedata, warnings
warnings.filterwarnings('ignore')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

# row0=節1(表頭合併), row1=節2, row2=節3, row3=節4, row4=中午skip,
# row5=節5, row6=節6, row7=節7, row8=節8, row9/10=skip,
# row11=節A, row12=節B, row13=節C, row14=節D
ROW_PERIOD = {0:'1', 1:'2', 2:'3', 3:'4', 5:'5', 6:'6', 7:'7', 8:'8', 11:'A', 12:'B', 13:'C', 14:'D'}
DAY_COL = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}
DAY_HEADERS = {'星期一','星期二','星期三','星期四','星期五','星期六','星期日'}

def is_room(s):
    # Room codes like MB209, G501, EB101, M203, L112, G502, N208
    return bool(re.match(r'^[A-Za-z]{1,3}\d{2,4}$', s.strip()))

def is_teacher(s):
    # Chinese name: 2-4 chars, all Chinese characters, possibly with ... suffix
    s = s.strip().rstrip('.')
    if not s:
        return False
    # Allow Chinese chars only (CJK range)
    return bool(re.match(r'^[\u2e80-\u2fff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]{2,5}$', s))

def clean_teacher(s):
    return s.strip().rstrip('.')

def clean_line(s):
    # Remove institution common period note (院共同時段 / 院共同時)
    s = re.sub(r'院共同時段?', '', s).strip()
    return s

def parse_cell(text):
    if not text or not text.strip():
        return None
    raw = nfc(text.strip())
    # Cell is purely a note → skip
    if re.fullmatch(r'院共同時段?', raw):
        return None

    lines = [clean_line(nfc(x.strip())) for x in raw.split('\n')]
    # Filter empty lines, isolated note remnants, and day header labels (from row0)
    lines = [l for l in lines if l and l != '段' and l not in DAY_HEADERS]
    if not lines:
        return None

    room = ''
    teacher = ''

    # Find room (last line matching room pattern)
    if lines and is_room(lines[-1]):
        room = lines.pop()

    # Find teacher (last remaining line, strip trailing dots)
    if lines and is_teacher(clean_teacher(lines[-1])):
        teacher = clean_teacher(lines.pop())

    course = ''.join(lines)
    if not course:
        return None
    return {'course': course, 'teacher': teacher, 'room': room}

results = []
log = []

with pdfplumber.open('data/班級課表.pdf') as pdf:
    for pi, page in enumerate(pdf.pages):
        try:
            text = nfc(page.extract_text() or '')
        except:
            text = ''
        m = re.search(r'班級[:：](.+?)(?:\s+\()', text)
        class_name = nfc(m.group(1).strip()) if m else f'page{pi}'

        try:
            tables = page.extract_tables()
        except:
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
                        'class': class_name,
                        'day': day,
                        'period': period,
                        'course': parsed['course'],
                        'teacher': parsed['teacher'],
                        'room': parsed['room']
                    })

        log.append(f'{class_name}: {len(entries)}')
        results.extend(entries)

log.append(f'TOTAL: {len(results)}')

with open('data/class_schedule_v2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open('data/extract2_log.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))
    f.write('\n\nSamples:\n')
    for r in results[:20]:
        f.write(str(r) + '\n')

print('Done')
