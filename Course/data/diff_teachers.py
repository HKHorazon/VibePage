import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/schedule.json', encoding='utf-8') as f:
    new = json.load(f)

with open('src/teachers.json', encoding='utf-8') as f:
    tm = json.load(f)
listed = set(tm.keys())

# Group new schedule by teacher
new_by_teacher = {}
for e in new:
    t = e['teacher']
    if t in listed:
        new_by_teacher.setdefault(t, set()).add((e['day'], e['period']))

# Teacher schedule from old extraction (hardcoded from original)
# Re-extract from teacher PDF using the same logic as before
# Instead, let's just print what we have per listed teacher
print('=== Schedule per listed teacher ===\n')
for teacher in sorted(listed):
    entries = [e for e in new if e['teacher'] == teacher]
    entries.sort(key=lambda e: (e['day'], e['period']))
    print(f'{teacher} ({len(entries)}):')
    for e in entries:
        print(f"  {e['day']}{e['period']} | {e['course'][:20]:<20} | {e['room']} | {e['class'][-6:]}")
    print()
