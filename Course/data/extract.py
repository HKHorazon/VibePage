import pdfplumber, json, re, unicodedata, warnings
warnings.filterwarnings('ignore')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

ROW_PERIOD = {1:'1', 2:'2', 3:'3', 4:'4', 6:'5', 7:'6', 8:'7', 9:'8', 12:'A', 13:'B', 14:'C', 15:'D'}
DAY_COL = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}

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
                parts = [x.strip() for x in cell.strip().split('\n') if x.strip()]
                if not parts:
                    continue
                entries.append({
                    'class': class_name,
                    'day': day,
                    'period': period,
                    'course': parts[0] if len(parts) > 0 else '',
                    'teacher': parts[1] if len(parts) > 1 else '',
                    'room': parts[2] if len(parts) > 2 else ''
                })

        log.append(f'{class_name}: {len(entries)}')
        results.extend(entries)

log.append(f'TOTAL: {len(results)}')

with open('data/class_schedule_raw.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open('data/extract_log.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))

print('Done')
