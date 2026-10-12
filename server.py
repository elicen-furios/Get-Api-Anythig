from flask import Flask, request, jsonify, render_template_string
import subprocess
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Anything Web UI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #38bdf8; text-align: center; font-size: 1.8rem; }
        .search-box { display: flex; gap: 10px; margin-bottom: 24px; }
        select, input, button { padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #fff; font-size: 15px; }
        input { flex: 1; }
        button { background: #0284c7; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #0369a1; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
        .card a { color: #38bdf8; text-decoration: none; font-size: 1.1rem; font-weight: 600; }
        .card a:hover { text-decoration: underline; }
        .meta { color: #94a3b8; font-size: 0.85rem; margin-top: 6px; }
        #loading { display: none; text-align: center; color: #38bdf8; font-weight: bold; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 API Anything Explorer</h1>
        <div class="search-box">
            <select id="site">
                <option value="hacker-news">Hacker News</option>
                <option value="youtube">YouTube</option>
            </select>
            <input type="text" id="query" placeholder="Enter search keyword..." value="python">
            <button onclick="fetchData()">Search</button>
        </div>

        <div id="loading">Searching... Please wait...</div>
        <div id="results"></div>
    </div>

    <script>
        async function fetchData() {
            const site = document.getElementById('site').value;
            const query = document.getElementById('query').value.trim();
            if (!query) return alert('Please enter a search query');

            const loading = document.getElementById('loading');
            const resultsDiv = document.getElementById('results');
            loading.style.display = 'block';
            resultsDiv.innerHTML = '';

            try {
                const res = await fetch(`/api/search?site=${site}&q=${encodeURIComponent(query)}`);
                const json = await res.json();
                loading.style.display = 'none';

                if (!json.ok) {
                    resultsDiv.innerHTML = `<p style="color:#ef4444;">Error: ${json.error || 'Failed to fetch'}</p>`;
                    return;
                }

                const list = json.data || [];
                if (list.length === 0) {
                    resultsDiv.innerHTML = '<p style="color:#94a3b8;">No results found.</p>';
                    return;
                }

                resultsDiv.innerHTML = list.map(item => `
                    <div class="card">
                        <a href="${item.url || '#'}" target="_blank">${item.title || item.name || 'Untitled'}</a>
                        <div class="meta">
                            ${item.author ? `By: ${item.author} | ` : ''}
                            ${item.points ? `Points: ${item.points} | ` : ''}
                            ${item.views ? `Views: ${item.views} | ` : ''}
                            ${item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                loading.style.display = 'none';
                resultsDiv.innerHTML = `<p style="color:#ef4444;">Request error: ${err.message}</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def search():
    site = request.args.get('site', 'hacker-news')
    q = request.args.get('q', 'python')

    # Query key mapping: Hacker News uses 'query', YouTube uses 'q'
    key_name = 'query' if site == 'hacker-news' else 'q'
    cmd = ["api-anything", "call", site, "search", f"{key_name}={q}"]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            parsed = json.loads(proc.stdout)
            return jsonify(parsed)
        else:
            return jsonify({"ok": False, "error": proc.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
