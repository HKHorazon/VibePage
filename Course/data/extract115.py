"""
extract115.py
解析 115-1 起的新版課表 PDF（每個檔案一位老師／一個班級，檔名即姓名／班級名）。

執行方式（從 Course/ 目錄下）：
    python data/extract115.py

輸入：
    data/115-1教師課表/*.pdf  → data/schedule_teacher.json
    data/115-1課表/*.pdf      → data/schedule_class.json
之後執行 data/merge.py 合併成 src/schedule.json
"""
import pdfplumber, json, re, unicodedata, sys, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

TEACHER_DIR = Path('data/115-1教師課表')
CLASS_DIR   = Path('data/115-1課表')

# 起始時刻 → 節次（1200 為午休，不列入）
PERIOD_BY_TIME = {
    '0810':'1', '0910':'2', '1010':'3', '1105':'4',
    '1250':'5', '1345':'6', '1440':'7', '1535':'8',
    '1635':'9', '1730':'10', '1820':'A', '1910':'B',
    '2000':'C', '2050':'D',
}
DAY_COL = {2:'一', 3:'二', 4:'三', 5:'四', 6:'五'}
NOISE = re.compile(r'^(時間|星期.|Office Hours|段)$')
COMMON = re.compile(r'院共同時段?')  # 「院共同時段」可能黏在教室後面，需整行掃除
ROOM_RE = re.compile(r'[A-Z]{1,5}\d{3,4}')
ROOM_ONLY_RE = re.compile(r'^[A-Za-z]{1,3}\d{2,4}$')
NAME_RE = re.compile(r'^[㐀-䶿一-鿿]{2,5}$')


def nk(s):
    """NFKC 正規化：把 PDF 的 CJK 部首字元（⼄⼤⽇）轉成正常漢字"""
    return unicodedata.normalize('NFKC', str(s or '')).strip()


def cell_lines(cell):
    lines = [COMMON.sub('', nk(x)).strip() for x in nk(cell).split('\n')]
    return [l for l in lines if l and not NOISE.match(l)]


def period_of(cell):
    m = re.search(r'(\d{2}):?(\d{2})', nk(cell))
    return PERIOD_BY_TIME.get(m.group(1) + m.group(2)) if m else None


def parse_teacher_cell(lines):
    """教師課表格子：課程 / 教室 / 班級（教室與班級可能同行）"""
    text = ''.join(lines)
    m = ROOM_RE.search(text)
    if m:
        course, room, klass = text[:m.start()], m.group(), text[m.end():]
    else:
        m2 = re.search(r'[日夜]四技', text)
        if m2:
            course, room, klass = text[:m2.start()], '', text[m2.start():]
        else:
            course, room, klass = text, '', ''
    course = course.strip()
    return {'course': course, 'room': room, 'class': klass.strip()} if course else None


def parse_class_cell(lines):
    """班級課表格子：課程 / 老師 / 教室（由後往前剝）"""
    lines = list(lines)
    room = lines.pop() if lines and ROOM_ONLY_RE.match(lines[-1]) else ''
    teacher = lines.pop().rstrip('.') if lines and NAME_RE.match(lines[-1].rstrip('.')) else ''
    course = ''.join(lines).strip()
    return {'course': course, 'teacher': teacher, 'room': room} if course else None


def fix_spill(col):
    """教師課表的格子文字有時會溢到下一列（班級名被切斷），把續行拉回來。
    正常格子一定以「…班」結尾；拉不回來就原樣保留，由 audit 列出讓人工確認。"""
    for i, lines in enumerate(col):
        if not lines or ''.join(lines).endswith('班'):
            continue
        follow = [c for c in col[i + 1:] if c]
        if not follow:
            continue
        nxt = follow[0]
        for take in range(1, min(3, len(nxt)) + 1):
            if ''.join(lines + nxt[:take]).endswith('班'):
                lines.extend(nxt[:take])
                del nxt[:take]
                break
    return col


def schedule_table(pdf_path):
    """新版 PDF 每頁兩個表格，第二個才是課表本體"""
    with pdfplumber.open(pdf_path) as pdf:
        tables = pdf.pages[0].extract_tables()
    return tables[-1] if tables else None


def extract(pdf_dir, kind):
    results, log = [], []
    for pdf_path in sorted(pdf_dir.glob('*.pdf')):
        name = pdf_path.stem
        table = schedule_table(pdf_path)
        if not table:
            log.append(f'{name}: 無表格')
            continue
        periods = [period_of(r[1] if len(r) > 1 else '') for r in table]
        entries = []
        for ci, day in DAY_COL.items():
            col = [cell_lines(r[ci]) if ci < len(r) else [] for r in table]
            if kind == 'teacher':
                fix_spill(col)
            for period, lines in zip(periods, col):
                if not period or not lines:
                    continue
                if kind == 'teacher':
                    p = parse_teacher_cell(lines)
                    if p:
                        entries.append({'teacher': name, 'day': day, 'period': period, **p})
                else:
                    p = parse_class_cell(lines)
                    if p:
                        entries.append({'teacher': p['teacher'], 'day': day, 'period': period,
                                        'course': p['course'], 'room': p['room'], 'class': name})
        log.append(f'{name}: {len(entries)}')
        results.extend(entries)
    print('\n'.join(log))
    return results


# 人工補正：PDF 本身資料有缺或有誤，每學期需重新確認
DROP_COURSES = {'產業實習', '專業實習'}  # 王瑋名，PDF 有但實際不排課


def fixup(entries):
    out = []
    for e in entries:
        if e['course'].lstrip('(*)') in DROP_COURSES:
            continue
        # PDF 把班級名截斷成「日四技妝」，教室 N209 被切到下一列
        if e['teacher'] == '林煒凱' and '科際整合' in e['course'] and not e['class']:
            e['class'], e['room'] = '日四技妝品系', 'N209'
        out.append(e)
    return out


def main():
    for pdf_dir, kind, out in ((TEACHER_DIR, 'teacher', 'data/schedule_teacher.json'),
                               (CLASS_DIR, 'class', 'data/schedule_class.json')):
        print(f'--- {pdf_dir}')
        data = fixup(extract(pdf_dir, kind))
        Path(out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'✓ 輸出 {out}（{len(data)} 筆）\n')


def demo():
    assert period_of('08:10\n|\n09:00') == '1'
    assert period_of('時間\n0810\n|\n0900') == '1'
    assert period_of('12:00|||12:50') is None  # 午休
    assert parse_teacher_cell(['提案與簡報技', '巧', 'MB211 日四技', '多遊系2年甲班']) == \
        {'course': '提案與簡報技巧', 'room': 'MB211', 'class': '日四技多遊系2年甲班'}
    assert parse_teacher_cell(['消費者心理學', '夜四技多遊', '系3年甲班']) == \
        {'course': '消費者心理學', 'room': '', 'class': '夜四技多遊系3年甲班'}
    assert parse_class_cell(['原畫設計', '王瑋名', 'G501']) == \
        {'course': '原畫設計', 'teacher': '王瑋名', 'room': 'G501'}
    assert parse_class_cell(['(*)網路社群經營', '與行銷', '凃聖忠']) == \
        {'course': '(*)網路社群經營與行銷', 'teacher': '凃聖忠', 'room': ''}
    assert cell_lines('星期一\n院共同時段') == []
    print('demo ok')


if __name__ == '__main__':
    demo() if '--test' in sys.argv else main()
