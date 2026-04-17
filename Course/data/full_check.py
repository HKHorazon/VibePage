import pdfplumber, json, re, unicodedata, warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

def nfc(s):
    return unicodedata.normalize('NFC', s) if s else ''

# Load existing data
with open('src/schedule.json', encoding='utf-8') as f:
    class_data = json.load(f)

# Print each class schedule summary with all entries
print('=== Class schedule extracted entries per class ===\n')

entry_by_class = {}
for e in class_data:
    k = e['class']
    entry_by_class.setdefault(k, []).append(e)

for cls, entries in entry_by_class.items():
    print(f'{cls} ({len(entries)} entries):')
    for e in entries:
        print(f"  {e['day']}{e['period']} | {e['course'][:20]:<20} | {e['teacher']:<5} | {e['room']}")
    print()
