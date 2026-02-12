from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage - now stores {name: {score: int, timestamp: str}}
scores = {}

# Load scores from file on startup
def load_scores():
    global scores
    filepath = '/Users/qingyao/vonMering/leaderboard/scores_export.json'
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                scores = json.load(f)
            print(f"Loaded {len(scores)} scores from {filepath}")
        except Exception as e:
            print(f"Error loading scores: {e}")

load_scores()

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
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Digital Cleanup Leaderboard</h1>       
        <h2> Christian von Mering group (2026 - 1st edition)  </h2>
        <h3>Submit Your Result</h3>
        <div class="input-group">
            <input id="name" placeholder="Enter your name" onkeypress="handleKeyPress(event)" />
            <input id="score" placeholder="cleaned GB" type="number" onkeypress="handleKeyPress(event)" />
            <button onclick="submitScore()">Submit</button>
        </div>

        <div class="leaderboard">
            <h3>Rankings</h3>
            <div id="leaderboard"></div>
        </div>
    </div>

    <script>
        async function loadScores() {
            const res = await fetch('/scores');
            const data = await res.json();
            const board = document.getElementById('leaderboard');

            board.innerHTML = '';
            data.forEach((row, index) => {
                const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(row.name)}&background=667eea&color=fff&size=128&rounded=true`;
                const timeAgo = new Date(row.timestamp);
                const timeStr = timeAgo.toLocaleString();
                board.innerHTML += `
                    <div class="score-item">
                        <div class="rank">#${index + 1}</div>
                        <img src="${avatarUrl}" alt="${row.name}" class="avatar" />
                        <div class="score-info">
                            <div class="score-name">${row.name}</div>
                            <div class="score-time">${timeStr}</div>
                        </div>
                        <div class="score-value">${row.score} GB</div>
                    </div>
                `;
            });
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                submitScore();
            }
        }

        async function submitScore() {
            const name = document.getElementById('name').value.trim();
            const score = document.getElementById('score').value.trim();

            if (!name || !score) {
                alert('Please enter both name and score');
                return;
            }

            await fetch('/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, score })
            });
            
            document.getElementById('name').value = '';
            document.getElementById('score').value = '';
            loadScores();
        }

        // Auto-save to server every 2 seconds
        setInterval(async () => {
            const res = await fetch('/scores');
            const data = await res.json();
            await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }, 2000);
        
        loadScores();
        setInterval(loadScores, 2000);
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
    data = request.json
    name = data["name"]
    score = round(float(data["score"]),3)
    
    scores[name] = {
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    return jsonify({"status": "ok"})

@app.route('/export', methods=['GET'])
def export():
    return scores

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    save_data = {item['name']: {'score': item['score'], 'timestamp': item['timestamp']} for item in data}
    filepath = '/Users/qingyao/vonMering/leaderboard/scores_export.json'
    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"Scores saved to {filepath}")
    return jsonify({"status": "saved"})

@app.route('/edit', methods=['GET','POST'])
def edit():
    # Support both JSON body and query parameters
    try:
        data = request.json
    except:
        data = request.args
    
    action = data.get("action")
    name = data.get("name")
    score = data.get("score")
    
    if not all([action, name, score]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    score = int(score)
    
    if action == "add":
        scores[name] = score
    elif action == "remove" and name in scores:
        del scores[name]
    elif action == "update" and name in scores:
        scores[name] = score    
    return scores

@app.route('/scores')
def get_scores():
    # sorted highest score first
    score_transform = [{'name': name, 'score': data['score'], 'timestamp': data['timestamp']} 
                      for name, data in scores.items()]
    sorted_scores = sorted(score_transform, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_scores)

if __name__ == '__main__':
    # run on local network
    app.run(host='0.0.0.0', port=5001, debug=True)
