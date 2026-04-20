"""
merge.py
合併 schedule_teacher.json + schedule_class.json → src/schedule.json

執行方式（從 Course/ 目錄下）：
    python data/merge.py
"""
import json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    return unicodedata.normalize('NFKC', s).strip() if s else ''

TEACHER_JSON = 'data/schedule_teacher.json'
CLASS_JSON   = 'data/schedule_class.json'
OUT_PATH     = 'src/schedule.json'

with open(TEACHER_JSON, encoding='utf-8') as f:
    teacher_data = json.load(f)

with open(CLASS_JSON, encoding='utf-8') as f:
    class_data = json.load(f)

# 以 (teacher, day, period) 為複合 key 去重
# 教師課表優先；班級課表補充教師課表沒有的項目
seen = set()
merged = []

def add_entry(e):
    teacher = norm(e.get('teacher',''))
    day     = norm(e.get('day',''))
    period  = norm(e.get('period',''))
    # 無老師時以班級一同作為 key，避免不同班級的空老師相互碰撞
    if teacher:
        key = (teacher, day, period)
    else:
        key = (teacher, day, period, norm(e.get('class','')))
    if key not in seen:
        seen.add(key)
        course = norm(e.get('course',''))
        optional = course.startswith('(*)')
        if optional:
            course = course[3:].lstrip()
        merged.append({
            'teacher':  teacher,
            'day':      day,
            'period':   period,
            'course':   course,
            'room':     norm(e.get('room','')),
            'class':    norm(e.get('class','')),
            'optional': optional,
        })

for e in teacher_data:
    add_entry(e)

added_from_class = 0
for e in class_data:
    before = len(merged)
    add_entry(e)
    if len(merged) > before:
        added_from_class += 1

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f'教師課表：{len(teacher_data)} 筆')
print(f'班級課表：{len(class_data)} 筆（補充 {added_from_class} 筆）')
print(f'合併結果：{len(merged)} 筆')
print(f'\n✓ 輸出 {OUT_PATH}')
