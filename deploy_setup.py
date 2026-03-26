import os
import shutil
import re

print("Starting restructuring...")

# Create directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
static_files = ['style.css', 'data.js']

# Move static files
for f in static_files:
    if os.path.exists(f):
        shutil.move(f, os.path.join('static', f))
        print(f"Moved {f} to static/")

# Move and update HTML files
for f in html_files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace css/js references
        content = re.sub(r'href="style\.css(\?v=\d+)?"', r'href="/static/style.css\1"', content)
        content = re.sub(r'src="data\.js(\?v=\d+)?"', r'src="/static/data.js\1"', content)
        
        # Write back to templates/
        dest = os.path.join('templates', f)
        with open(dest, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Remove original
        os.remove(f)
        print(f"Moved and updated {f} to templates/")

# Update data.js API_BASE_URL
data_js_path = os.path.join('static', 'data.js')
if os.path.exists(data_js_path):
    with open(data_js_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Change 'http://127.0.0.1:5000' to '' (relative path)
    content = content.replace("const API_BASE_URL = 'http://127.0.0.1:5000';", "const API_BASE_URL = '';")
    
    with open(data_js_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print("Updated data.js API_BASE_URL")

print("Restructuring complete!")
