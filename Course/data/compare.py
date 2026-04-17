import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/schedule.json', encoding='utf-8') as f:
    old = json.load(f)

with open('data/class_schedule_v2.json', encoding='utf-8') as f:
    new = json.load(f)

print(f'Old schedule: {len(old)} entries (teacher-based)')
print(f'New schedule: {len(new)} entries (class-based)')

# Entries in new but missing teacher
no_teacher = [e for e in new if not e['teacher']]
print(f'\nEntries with no teacher: {len(no_teacher)}')
for e in no_teacher:
    print(f"  {e['class']} {e['day']}{e['period']} {e['course']}")

# All unique teachers in new data
teachers_new = sorted(set(e['teacher'] for e in new if e['teacher']))
print(f'\nTeachers in class schedule ({len(teachers_new)}):')
for t in teachers_new:
    print(f'  {t}')
