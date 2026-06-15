"""Fix Unicode characters in all pipeline files"""
import os
import glob

replacements = {
    '✓': '[OK]',
    '✗': '[ERROR]',
    '⊙': '[SKIP]',
    '📡': '[SCRAPER]',
    '📥': '[DOWNLOAD]',
    '📄': '[PDF]',
    '🤖': '[AI]',
    '🔄': '[PROCESS]',
    '→': '-->',
    '═': '=',
    '💬': '[CHAT]',
    '🔍': '[SEARCH]',
    '📋': '[ANSWER]',
    '📌': '[SOURCES]',
}

files = glob.glob('pipeline/*.py') + ['run_pipeline_test.py']

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
        else:
            print(f"OK: {filepath}")
    except Exception as e:
        print(f"Error with {filepath}: {e}")

print("\nDone!")
