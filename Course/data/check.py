import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/schedule.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total entries: {len(data)}\n')

print('=== Entries with no teacher (but has room) ===')
for i, e in enumerate(data):
    if not e['teacher']:
        print(f"  [{i}] {e['class']} {e['day']}{e['period']} | {e['course']} | room={e['room']}")

print('\n=== Short course names (<=4 chars, suspicious) ===')
for i, e in enumerate(data):
    c = e['course']
    if len(c) <= 4 and c and not c.startswith('('):
        print(f"  [{i}] {e['class']} {e['day']}{e['period']} | course={c!r} | teacher={e['teacher']} | room={e['room']}")

print('\n=== Entries where course looks wrong (contains room pattern) ===')
import re
for i, e in enumerate(data):
    # Course should not look like a room code
    if re.search(r'[A-Z]{1,3}\d{2,4}', e['course']):
        print(f"  [{i}] {e['class']} {e['day']}{e['period']} | course={e['course']!r} | teacher={e['teacher']} | room={e['room']}")
