from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import random
import os # পোর্ট ব্যবহারের জন্য

# Flask অ্যাপ ইনিশিয়ালাইজ করা হয়েছে
app = Flask(__name__)

# --- চ্যাটবট ইন্টারফেস (HTML/CSS/JS) ---
# সম্পূর্ণ ফ্রন্টএন্ড কোড
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ইন্টারনেট সার্চ বট</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background-color: #de5833; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 85%; padding: 12px 16px; border-radius: 15px; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
        .user-msg { align-self: flex-end; background-color: #de5833; color: white; border-bottom-right-radius: 2px; }
        .bot-msg { align-self: flex-start; background-color: white; color: #333; border: 1px solid #ddd; border-bottom-left-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        
        /* সার্চ রেজাল্ট ডিজাইন */
        .result-item { margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
        .result-item:last-child { border-bottom: none; }
        .result-title { color: #1a0dab; font-weight: bold; text-decoration: none; font-size: 16px; display: block; }
        .result-title:hover { text-decoration: underline; }
        .result-link { color: #006621; font-size: 12px; display: block; margin-bottom: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .result-desc { color: #545454; font-size: 14px; }
        
        .input-area { background: white; padding: 10px; display: flex; gap: 10px; border-top: 1px solid #ddd; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; outline: none; font-size: 16px; }
        button { background-color: #de5833; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; font-weight: bold; }
        button:disabled { background-color: #ccc; }
        .loader { text-align: center; color: #666; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>

<div class="header">Internet Search Bot</div>

<div class="chat-container" id="chatBox">
    <div class="message bot-msg">
        হ্যালো! আমি আপনার ইন্টারনেট সার্চ অ্যাসিস্ট্যান্ট। আপনি কী জানতে চান?
    </div>
</div>

<div class="input-area">
    <input type="text" id="userInput" placeholder="এখানে প্রশ্ন লিখুন..." onkeypress="if(event.key === 'Enter') sendMessage()">
    <button onclick="sendMessage()" id="sendBtn">Search</button>
</div>

<script>
    async function sendMessage() {
        const input = document.getElementById('userInput');
        const chatBox = document.getElementById('chatBox');
        const btn = document.getElementById('sendBtn');
        const query = input.value.trim();

        if (!query) return;

        chatBox.innerHTML += `<div class="message user-msg">${query}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;
        
        const loadingId = 'loading-' + Date.now();
        chatBox.innerHTML += `<div class="loader" id="${loadingId}">ইন্টারনেটে খোঁজা হচ্ছে...</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
        btn.disabled = true;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            });
            
            const data = await response.json();
            document.getElementById(loadingId).remove();

            if (data.results && data.results.length > 0) {
                let resultHTML = "<strong>আমি যা তথ্য পেলাম:</strong><br><br>";
                
                data.results.forEach(item => {
                    resultHTML += `
                        <div class="result-item">
                            <a href="${item.link}" target="_blank" class="result-title">${item.title}</a>
                            <span class="result-link">${item.link}</span>
                            <div class="result-desc">${item.desc}</div>
                        </div>
                    `;
                });
                
                chatBox.innerHTML += `<div class="message bot-msg">${resultHTML}</div>`;
            } else {
                chatBox.innerHTML += `<div class="message bot-msg">কোনো তথ্য পাওয়া যায়নি। অন্যভাবে প্রশ্ন করে দেখুন।</div>`;
            }

        } catch (e) {
            document.getElementById(loadingId).remove();
            chatBox.innerHTML += `<div class="message bot-msg">সার্ভার এরর হয়েছে।</div>`;
        }

        btn.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>

</body>
</html>
"""

# --- DuckDuckGo সার্চ লজিক ---
def search_web(query):
    # আমরা DuckDuckGo এর HTML ভার্সন ব্যবহার করব যা খুব হালকা এবং দ্রুত এবং ব্লক করে না
    url = "https://html.duckduckgo.com/html/"
    
    payload = {'q': query}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # রেজাল্টগুলো লুপ করা
            for result in soup.find_all('div', class_='result'):
                # টাইটেল ও লিংক বের করা
                link_tag = result.find('a', class_='result__a')
                if not link_tag: continue
                
                title = link_tag.text
                link = link_tag['href']
                
                # ডেসক্রিপশন বের করা
                snippet_tag = result.find('a', class_='result__snippet')
                desc = snippet_tag.text if snippet_tag else "বিবরণ পাওয়া যায়নি"
                
                if link and title:
                    results.append({
                        'title': title,
                        'link': link,
                        'desc': desc
                    })
                    
                # সর্বোচ্চ ৫টি রেজাল্ট নেওয়া
                if len(results) >= 5:
                    break
                    
            return results
        else:
            print(f"Search failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in search_web: {e}")
        return []

# --- সার্ভার রুট ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_api():
    data = request.json
    query = data.get('query', '')
    results = search_web(query)
    return jsonify({'results': results})

if __name__ == '__main__':
    # ক্লাউড সার্ভারের জন্য dynamic port ব্যবহার করা
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

