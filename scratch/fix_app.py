import os

path = r'c:\Git\WysiWyg - Copy (2)\app.js'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the last });
for i in range(len(lines)-1, -1, -1):
    if lines[i].strip() == '});':
        # Check if it's the end of DOMContentLoaded
        # We'll just insert before the last line
        lines.insert(i, '    document.getElementById(\'updateConditionsBtn\')?.addEventListener(\'click\', (e) => {\n')
        lines.insert(i+1, '        e.preventDefault();\n')
        lines.insert(i+2, '        mergeConditions();\n')
        lines.insert(i+3, '    });\n\n')
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated app.js")
