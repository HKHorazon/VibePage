import pdfplumber, json, re, unicodedata, warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

# Find 日四技多遊系1年乙班 page index
with pdfplumber.open('data/班級課表.pdf') as pdf:
    for pi in range(len(pdf.pages)):
        page = pdf.pages[pi]
        text = nfc(page.extract_text() or '')
        m = re.search(r'班級[:：](.+?)(?:\s+\()', text)
        cls = nfc(m.group(1).strip()) if m else ''
        if '1年⼄' in cls or '1年乙' in cls:
            tables = page.extract_tables()
            if not tables:
                continue
            t = tables[0]
            print(f'=== {cls} (page {pi}): {len(t)} rows ===')
            for ri, row in enumerate(t):
                first = nfc(str(row[0] or ''))[:20].replace('\n','|')
                content = {}
                for ci in range(2, min(7, len(row))):
                    c = nfc(str(row[ci] or ''))
                    if c.strip() and c.strip() != 'None':
                        content[ci] = c[:40].replace('\n','|')
                if content or ri in [0,1,2,3,4,5,6,7,8]:
                    print(f'  row{ri}: {first!r}  {content}')
