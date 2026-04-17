import pdfplumber, json, re, unicodedata, warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

# Check row count per page and what's in each row
with pdfplumber.open('data/班級課表.pdf') as pdf:
    for pi in [0, 2, 6]:  # check a few pages
        page = pdf.pages[pi]
        text = nfc(page.extract_text() or '')
        m = re.search(r'班級[:：](.+?)(?:\s+\()', text)
        cls = nfc(m.group(1).strip()) if m else f'page{pi}'
        tables = page.extract_tables()
        if not tables:
            continue
        t = tables[0]
        print(f'\n=== {cls}: {len(t)} rows ===')
        for ri, row in enumerate(t):
            # Show row index, first col, and any non-empty content cells
            first = nfc(str(row[0] or ''))[:20].replace('\n','|')
            content = []
            for ci in range(2, min(7, len(row))):
                c = nfc(str(row[ci] or ''))
                if c.strip() and c.strip() != 'None':
                    content.append(f'col{ci}: {c[:30].replace(chr(10),"|")!r}')
            print(f'  row{ri}: [{first!r}] {" | ".join(content)}')
