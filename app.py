from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage - now stores {name: {cleaned_gb: float, timestamp: str, location: str, starting_gb: float}}
data = {}

# Load data from file on startup
def load_data():
    global data
    filepath = './data_export.json'
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} entries from {filepath}")
        except Exception as e:
            print(f"Error loading data: {e}")

load_data()

# HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Leaderboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h2 {
            color: #555;
            text-align: center;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        h3 {
            color: #777;
            text-align: left;
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .leaderboard {
            margin-top: 30px;
        }
        
        .score-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .score-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            margin-right: 15px;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        
        .score-info {
            flex: 1;
        }
        
        .score-name {
            font-weight: 600;
            color: #333;
            font-size: 16px;
        }
        
        .score-time {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }
        
        .score-value {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .rank {
            font-size: 28px;
            font-weight: 700;
            color: #667eea;
            margin-right: 15px;
            min-width: 40px;
        }

        .references {
            position: fixed;
            right: 20px;
            bottom: 20px;
            display: flex;
            gap: 12px;
            font-size: 13px;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 12px;
            border-radius: 999px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(6px);
        }

        .references a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }

        .references a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Digital Cleanup Leaderboard</h1>       
        <h2> Christian von Mering group (2026 - 1st edition)  </h2>
        <h3>Submit Your Result</h3>
        <div class="input-group">
            <input id="name" placeholder="Enter your name" onkeypress="handleKeyPress(event)" />
            <input id="location" placeholder="Location" onkeypress="handleKeyPress(event)" />
        </div>
        <div class="input-group">
            <input id="starting" placeholder="Starting GB" type="number" step="0.001" onkeypress="handleKeyPress(event)" />
            <input id="cleaned" placeholder="Cleaned GB" type="number" step="0.001" onkeypress="handleKeyPress(event)" />
            <button onclick="submitData()">Submit</button>
        </div>

        <div class="leaderboard">
            <h3>Rankings</h3>
            <div id="leaderboard"></div>
        </div>
    </div>

    <div class="references">
        <a href="https://docs.google.com/document/d/1mr3Gtoizlf2rpxz_tFaiZzyI7oSHGOQOY_obTiULrgg/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Guideline and tips</a>
        <a href="https://docs.google.com/spreadsheets/d/10NuOfhl-iueRPImkrWnIAhcJ3drBa00A8-DTUd0q2So/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Current usage</a>
        <a href="https://docs.google.com/spreadsheets/d/1W9oHgotx9LIF_r-roZJfcK00D1f3-IXTtV1zNIywH5I/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Tape storage</a>
        <a href="https://docs.google.com/spreadsheets/d/1G1M5u6J2VZJaH2sTVQhNZQ9g1cEgj77cc8wl0GkhJqI/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Archival queue</a>
    </div>

    <script>
        async function loadData() {
            const res = await fetch('/data');
            const entries = await res.json();
            const board = document.getElementById('leaderboard');

            board.innerHTML = '';
            entries.forEach((row, index) => {
                const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(row.name)}&background=667eea&color=fff&size=128&rounded=true`;
                const timeAgo = new Date(row.timestamp);
                const timeStr = timeAgo.toLocaleString();
                const percentage = row.starting_gb > 0 ? ((row.cleaned_gb / row.starting_gb) * 100).toFixed(1) : 0;
                board.innerHTML += `
                    <div class="score-item">
                        <div class="rank">#${index + 1}</div>
                        <img src="${avatarUrl}" alt="${row.name}" class="avatar" />
                        <div class="score-info">
                            <div class="score-name">${row.name} ${row.location ? '(' + row.location + ')' : ''}</div>
                            <div class="score-time">${timeStr}</div>
                            <div class="score-time">Started: ${row.starting_gb} GB → Cleaned: ${row.cleaned_gb} GB (${percentage}%)</div>
                        </div>
                        <div class="score-value">${percentage}%</div>
                    </div>
                `;
            });
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                submitScore();
            }
        }

        async function submitData() {
            const name = document.getElementById('name').value.trim();
            const location = document.getElementById('location').value.trim();
            const starting = document.getElementById('starting').value.trim();
            const cleaned = document.getElementById('cleaned').value.trim();

            if (!name || !starting || !cleaned) {
                alert('Please enter name, starting GB, and cleaned GB');
                return;
            }

            await fetch('/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, location, starting_gb: starting, cleaned_gb: cleaned })
            });
            
            document.getElementById('name').value = '';
            document.getElementById('location').value = '';
            document.getElementById('starting').value = '';
            document.getElementById('cleaned').value = '';
            loadData();
        }

        // Auto-save to server every 2 seconds
        setInterval(async () => {
            const res = await fetch('/data');
            const entries = await res.json();
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(entries)
            });
        }, 2000);
        
        loadData();
        setInterval(loadData, 2000);
    </script>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    request_data = request.json
    name = request_data["name"]
    cleaned_gb = round(float(request_data["cleaned_gb"]),3)
    location = request_data.get("location", "")
    starting_gb = round(float(request_data.get("starting_gb", 0)),3)
    
    data[name] = {
        "cleaned_gb": cleaned_gb,
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "starting_gb": starting_gb
    }
    return jsonify({"status": "ok"})

@app.route('/export', methods=['GET'])
def export():
    return data

@app.route('/save', methods=['POST'])
def save():
    request_data = request.json
    save_data = {item['name']: {'cleaned_gb': item['cleaned_gb'], 'timestamp': item['timestamp'], 'location': item.get('location', ''), 'starting_gb': item.get('starting_gb', 0)} for item in request_data}
    filepath = './data_export.json'
    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"Data saved to {filepath}")
    return jsonify({"status": "saved"})

@app.route('/edit', methods=['GET','POST'])
def edit():
    # Support both JSON body and query parameters
    try:
        request_data = request.json
    except:
        request_data = request.args
    
    action = request_data.get("action")
    name = request_data.get("name")
    cleaned_gb = request_data.get("cleaned_gb")
    
    if not all([action, name, cleaned_gb]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    cleaned_gb = int(cleaned_gb)
    
    if action == "add":
        data[name] = cleaned_gb
    elif action == "remove" and name in data:
        del data[name]
    elif action == "update" and name in data:
        data[name] = cleaned_gb    
    return data

@app.route('/data')
def get_data():
    # sorted highest cleaned_gb first
    entries = [{'name': name, 'cleaned_gb': entry['cleaned_gb'], 'timestamp': entry['timestamp'], 'location': entry.get('location', ''), 'starting_gb': entry.get('starting_gb', 0)} for name, entry in data.items()]
    sorted_entries = sorted(entries, key=lambda x: x['cleaned_gb'], reverse=True)
    return jsonify(sorted_entries)

if __name__ == '__main__':
    # run on local network
    app.run(host='0.0.0.0', port=5001, debug=True)
