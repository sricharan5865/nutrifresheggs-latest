import sys, re
from pathlib import Path

css_files = ['styles.css', 'css/style.css']
for cf in css_files:
    if not Path(cf).exists():
        continue
    txt = open(cf, encoding='utf-8').read()
    matches = re.findall(r'url\((.*?)\)', txt)
    print(f"{cf}: {len(matches)} urls found")
    for m in matches:
        cleaned = m.strip('\'" ')
        if not cleaned.startswith('data:') and not cleaned.startswith('http'):
            p1 = (Path(cf).parent / cleaned).resolve()
            p2 = (Path('.') / cleaned).resolve()
            if not p1.exists() and not p2.exists():
                print(f"  MISSING in {cf}: {cleaned}")
