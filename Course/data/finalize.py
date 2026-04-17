import json, shutil

with open('data/class_schedule_v2.json', encoding='utf-8') as f:
    data = json.load(f)

# Reorder fields to match expected format: teacher, day, period, course, room, class
ordered = []
for e in data:
    ordered.append({
        'teacher': e['teacher'],
        'day': e['day'],
        'period': e['period'],
        'course': e['course'],
        'room': e['room'],
        'class': e['class']
    })

with open('src/schedule.json', 'w', encoding='utf-8') as f:
    json.dump(ordered, f, ensure_ascii=False, indent=2)

print(f'Written {len(ordered)} entries to src/schedule.json')

# Show unique non-listed teachers
with open('src/teachers.json', encoding='utf-8') as f:
    teachers_map = json.load(f)
listed = set(teachers_map.keys())

non_listed = sorted(set(e['teacher'] for e in ordered if e['teacher'] and e['teacher'] not in listed))
print(f'\nNon-listed teachers ({len(non_listed)}):')
for t in non_listed:
    print(f'  {t}')
