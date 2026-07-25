import os

file_path = 'templates/core/view_attendance_student.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('|default: ', '|default:')
new_content = new_content.replace('|default :', '|default:')
# Just in case for other potential spacing issues
new_content = new_content.replace(' |default', '|default')

if content != new_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("FIXED: Replaced 'default: ' with 'default:'")
else:
    print("NO CHANGES: File already clean?")

# Verification
with open(file_path, 'r', encoding='utf-8') as f:
    final_content = f.read()
    if '|default: ' in final_content:
        print("ERROR: Still found '|default: '")
    else:
        print("VERIFIED: No '|default: ' found.")
