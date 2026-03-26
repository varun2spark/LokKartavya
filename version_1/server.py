import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS
import wikipedia

app = Flask(__name__)
CORS(app)

# --- IN-MEMORY STORAGE (For MVP Demo) ---
# In a real app, use a database like SQLite or Firebase.
submitted_reports = []

# --- 1. HELPER: GET WIKIPEDIA DATA ---
def get_wiki_data(name):
    try:
        print(f"📖 Searching Wikipedia for: {name}...")
        wiki_page = wikipedia.page(name, auto_suggest=True)
        bio = wikipedia.summary(name, sentences=3)
        
        image_url = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
        if wiki_page.images:
            for img in wiki_page.images:
                ext = img.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png'] and 'icon' not in img.lower():
                    image_url = img
                    break
        
        return {"wiki_name": wiki_page.title, "bio": bio, "image": image_url}
    except Exception as e:
        print(f"⚠️ Wiki Error: {e}")
        return {"wiki_name": name, "bio": "Official bio not available.", "image": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"}

# --- 2. HELPER: GET MYNETA DATA ---
def get_myneta_data(name):
    try:
        print(f"🦆 Searching MyNeta for: {name}...")
        query = f"site:myneta.info {name} candidate criminal cases"
        results = list(DDGS().text(query, max_results=1))
        
        if not results:
            return None
            
        target_url = results[0]['href']
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {"source_url": target_url}

        # Criminal Cases
        criminal_text = soup.find(string=re.compile(r'Criminal Case', re.IGNORECASE))
        if criminal_text:
            val = criminal_text.parent.find_next('span').text.strip()
            data['criminal_cases'] = val if val else "0"
        else:
            data['criminal_cases'] = "0"

        # Assets
        assets_text = soup.find(string=re.compile(r'Total Assets', re.IGNORECASE))
        if assets_text:
            raw_assets = assets_text.find_parent('tr').find_all('td')[-1].text.strip()
            data['assets'] = raw_assets.split('~')[0].strip()
        else:
            data['assets'] = "Data Unavailable"
            
        return data

    except Exception as e:
        print(f"Error fetching MyNeta: {e}")
        return None

# --- API ENDPOINTS ---

@app.route('/api/search-leader', methods=['GET'])
def search_leader():
    query = request.args.get('name')
    if not query:
        return jsonify({"error": "No name provided"}), 400

    wiki_data = get_wiki_data(query)
    myneta_data = get_myneta_data(query)
    
    if not myneta_data:
        myneta_data = {
            "criminal_cases": "Unknown",
            "assets": "Check Official Affidavit",
            "source_url": "https://www.myneta.info"
        }

    return jsonify({
        "name": wiki_data['wiki_name'],
        "bio": wiki_data['bio'],
        "image": wiki_data['image'],
        "criminal_cases": myneta_data['criminal_cases'],
        "assets": myneta_data['assets'],
        "source_url": myneta_data['source_url']
    })

@app.route('/api/report-issue', methods=['POST'])
def report_issue():
    # Feature 8: Civic Issue Documentation
    data = request.json
    data['id'] = len(submitted_reports) + 1
    data['status'] = 'Verified by AI'
    submitted_reports.append(data)
    print(f"📝 New Report Received: {data}")
    return jsonify({"message": "Report submitted successfully", "report_id": data['id']})

@app.route('/api/simplify', methods=['POST'])
def simplify_text():
    # Feature 7: AI Simplification (Simulated for speed/reliability in MVP)
    # In a real production app, you would call Gemini/OpenAI API here.
    time.sleep(1) # Simulate AI processing delay
    return jsonify({
        "simplified": "An MLA acts like a voice for their local area. They help make laws, approve spending for development, and solve problems for the people who elected them."
    })

if __name__ == '__main__':
    print("🚀 LokKartavya Server Running on Port 5000...")
    app.run(debug=True, port=5000)
