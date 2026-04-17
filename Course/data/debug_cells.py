import pdfplumber, unicodedata, warnings, sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

ROW_PERIOD = {1:'1', 2:'2', 3:'3', 4:'4', 6:'5', 7:'6', 8:'7', 9:'8', 12:'A', 13:'B', 14:'C', 15:'D'}
DAY_COL = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}

# Show page 8 (日四技多遊系3年甲班) cell for 一1
with pdfplumber.open('data/班級課表.pdf') as pdf:
    for pi in [7, 8, 9, 10, 11, 12, 13]:  # pages for 日四技 classes
        page = pdf.pages[pi]
        import re
        text = nfc(page.extract_text() or '')
        m = re.search(r'班級[:：](.+?)(?:\s+\()', text)
        class_name = nfc(m.group(1).strip()) if m else f'page{pi}'

        tables = page.extract_tables()
        if not tables:
            continue
        table = tables[0]

        # Show row 1 (period 1) cells
        for row_i in [1]:
            if row_i >= len(table):
                continue
            row = table[row_i]
            print(f'\n{class_name} period 1:')
            for col_i, day in DAY_COL.items():
                if col_i >= len(row):
                    continue
                cell = nfc(str(row[col_i]) if row[col_i] else '')
                if cell.strip() and cell.strip() != 'None':
                    print(f'  {day}: {repr(cell)}')
