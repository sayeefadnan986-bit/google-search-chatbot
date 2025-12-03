from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineFreak & Google Explorer</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Hind+Siliguri:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --text-light: #ffffff;
            --text-dark: #e0e0e0;
            --accent-color: #00f2fe;
            --cinefreak-color: #ff5722;
            --general-color: #4CAF50;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Poppins', 'Hind Siliguri', sans-serif;
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                        url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-attachment: fixed;
            height: 100vh;
            display: flex;
            flex-direction: column;
            color: var(--text-light);
            overflow: hidden;
        }

        .header {
            background: rgba(20, 20, 20, 0.85);
            backdrop-filter: blur(15px);
            padding: 15px 20px;
            text-align: center;
            border-bottom: 1px solid var(--glass-border);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            z-index: 100;
        }

        .header h1 {
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(to right, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }

        .branding-tag {
            font-size: 12px;
            color: #aaa;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            scroll-behavior: smooth;
        }

        .chat-container::-webkit-scrollbar { width: 6px; }
        .chat-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }

        .message {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 18px;
            font-size: 15px;
            line-height: 1.6;
            position: relative;
            animation: fadeIn 0.4s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .user-msg {
            align-self: flex-end;
            background: var(--primary-gradient);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot-msg {
            align-self: flex-start;
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            color: var(--text-dark);
            border-bottom-left-radius: 4px;
        }

        .result-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 12px;
            margin-top: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s;
        }
        .result-card:hover { transform: translateY(-2px); background: rgba(0, 0, 0, 0.5); }
        
        .result-title {
            color: var(--accent-color);
            font-weight: 600;
            text-decoration: none;
            display: block;
            margin-bottom: 5px;
            font-size: 16px;
        }
        .result-link { font-size: 11px; color: #888; display: block; margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .result-desc { font-size: 13px; color: #ccc; }
        
        .source-tag {
            font-size: 10px;
            padding: 3px 6px;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 8px;
            color: #111;
        }
        .source-cinefreak { background-color: var(--cinefreak-color); }
        .source-general { background-color: var(--general-color); }

        .input-area {
            background: rgba(20, 20, 20, 0.9);
            backdrop-filter: blur(20px);
            padding: 15px;
            display: flex;
            gap: 15px;
            border-top: 1px solid var(--glass-border);
            align-items: center;
        }

        input {
            flex: 1;
            padding: 14px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.05);
            color: white;
            font-size: 16px;
            outline: none;
            transition: 0.3s;
        }
        input:focus { border-color: var(--accent-color); background: rgba(255,255,255,0.1); box-shadow: 0 0 15px rgba(0, 242, 254, 0.2); }

        button {
            background: var(--primary-gradient);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(118, 75, 162, 0.5);
            transition: 0.3s;
        }
        button:hover { transform: scale(1.1); box-shadow: 0 0 30px rgba(118, 75, 162, 0.8); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }

        .footer {
            text-align: center;
            padding: 8px;
            font-size: 11px;
            color: #666;
            background: #000;
            border-top: 1px solid #222;
        }
        .footer a { color: #888; text-decoration: none; }
        .warning-text { color: #ff4757; font-weight: bold; }

        .typing-indicator span {
            display: inline-block; width: 6px; height: 6px; background-color: #fff; border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out both; margin: 0 2px;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

    </style>
</head>
<body>

<div class="header">
    <h1>CineFreak & Google Explorer</h1>
    <div class="branding-tag">Build by Sayeef Adnan</div>
</div>

<div class="chat-container" id="chatBox">
    <div class="message bot-msg">
        <div style="font-weight:bold; color:var(--accent-color); margin-bottom:8px;">বিসমিল্লাহির রহমানির রহিম</div>
        আসসালামু আলাইকুম! আমি <strong>CineFreak</strong> এবং <strong>Google</strong> সার্চ অ্যাসিস্ট্যান্ট।<br><br>
        মুভি বা সিরিজের নাম লিখলে CineFreak-এ খুঁজব, আর সাধারণ প্রশ্ন করলে Google-এ খুঁজব।
    </div>
</div>

<div class="input-area">
    <input type="text" id="userInput" placeholder="মুভির নাম বা আপনার প্রশ্ন লিখুন..." autocomplete="off" onkeypress="if(event.key === 'Enter') sendMessage()">
    <button onclick="sendMessage()" id="sendBtn">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
    </button>
</div>

<div class="footer">
    <div class="warning-text">⚠️ Warning: Copying Adnan's website without permission is a punishable offense.</div>
    <div>Website developed by <strong>Sayeef Adnan</strong>. Websiteটি ব্যবহারের জন্য আপনাকে অশেষ ধন্যবাদ।</div>
    <div>যোগাযোগ: <a href="mailto:iamadtul@gmail.com">iamadtul@gmail.com</a></div>
</div>

<script>
    async function sendMessage() {
        const input = document.getElementById('userInput');
        const chatBox = document.getElementById('chatBox');
        const btn = document.getElementById('sendBtn');
        const query = input.value.trim();

        if (!query) return;

        // User Message
        chatBox.innerHTML += `<div class="message user-msg">${query}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Loader
        const loadingId = 'loading-' + Date.now();
        const loaderHTML = `<div class="message bot-msg" id="${loadingId}">
                                <div class="typing-indicator"><span></span><span></span><span></span></div>
                            </div>`;
        chatBox.insertAdjacentHTML('beforeend', loaderHTML);
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

            let botResponseHTML = `<div style="font-weight:bold; color:var(--accent-color); margin-bottom:5px;">বিসমিল্লাহির রহমানির রহিম</div>`;

            if (data.results && data.results.length > 0) {
                const sourceClass = data.source === 'CineFreak' ? 'source-cinefreak' : 'source-general';
                const sourceLabel = data.source === 'CineFreak' ? 'সোর্স: CineFreak.net (স্পেশালাইজড)' : 'সোর্স: Google (সাধারণ)';

                botResponseHTML += `<span class="source-tag ${sourceClass}">${sourceLabel}</span><br>`;
                botResponseHTML += `আপনার জন্য ${data.results.length} টি ফলাফল পাওয়া গেছে:<br>`;
                
                data.results.forEach(item => {
                    botResponseHTML += `
                        <div class="result-card">
                            <a href="${item.link}" target="_blank" class="result-title">${item.title}</a>
                            <span class="result-link">${item.link}</span>
                            <div class="result-desc">${item.desc}</div>
                        </div>
                    `;
                });
            } else {
                botResponseHTML += `দুঃখিত, '${query}' সম্পর্কিত কোনো তথ্য খুঁজে পাওয়া যায়নি।`;
            }

            // Footer Signature in Message
            botResponseHTML += `<br><div style="margin-top:15px; padding-top:10px; border-top:1px dashed #444; font-size:12px; color:#888;">
                                    <i>Build by Sayeef Adnan</i><br>
                                    <span style="color:#ff6b6b; font-size:10px;">Copying Adnan's website without permission is a punishable offense.</span>
                                </div>`;

            chatBox.innerHTML += `<div class="message bot-msg">${botResponseHTML}</div>`;

        } catch (e) {
            document.getElementById(loadingId).remove();
            chatBox.innerHTML += `<div class="message bot-msg" style="color:#ff6b6b;">
                                    সার্ভার এরর হয়েছে। দয়া করে যোগাযোগ করুন: <a href="mailto:iamadtul@gmail.com" style="color:#ff6b6b; text-decoration:underline;">iamadtul@gmail.com</a>
                                  </div>`;
        }

        btn.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>

</body>
</html>
"""

def search_cinefreak(query):
    """
    CineFreak.net থেকে তথ্য খুঁজে বের করার ফাংশন।
    """
    url = f"https://www.cinefreak.net/?s={urllib.parse.quote_plus(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('div', class_='post')

            for post in articles:
                title_tag = post.find('h2') or post.find('h3') or post.find('h1')
                link_tag = post.find('a')
                desc_tag = post.find('div', class_='entry-content') or post.find('div', class_='post-summary')
                
                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    link = link_tag['href']
                    desc = desc_tag.text.strip()[:100] + "..." if desc_tag else "বিস্তারিত দেখতে লিংকে ক্লিক করুন..."
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'desc': desc
                    })
            
            return results[:5]
        else:
            return []
    except Exception as e:
        print(f"Error scraping CineFreak: {e}")
        return []

def search_web(query):
    """
    সাধারণ ইন্টারনেট সার্চ (DuckDuckGo) যা Google 429 ব্লক এড়িয়ে যায়।
    """
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
            
            for result in soup.find_all('div', class_='result'):
                link_tag = result.find('a', class_='result__a')
                if not link_tag:
                    continue
                
                title = link_tag.text
                link = link_tag['href']
                
                snippet_tag = result.find('a', class_='result__snippet')
                desc = snippet_tag.text if snippet_tag else "বিবরণ পাওয়া যায়নি"
                
                if link and title:
                    results.append({
                        'title': title,
                        'link': link,
                        'desc': desc
                    })
                    
                if len(results) >= 5:
                    break
                    
            return results
        else:
            return []
    except Exception as e:
        print(f"Error in search_web (DuckDuckGo): {e}")
        return []

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_api():
    data = request.json
    query = data.get('query', '')
    
    # প্রথমে CineFreak-এ সার্চ করা
    cinefreak_results = search_cinefreak(query)
    
    if cinefreak_results:
        # CineFreak-এ ফলাফল পাওয়া গেলে সেটি রিটার্ন
        return jsonify({'results': cinefreak_results, 'source': 'CineFreak'})
    else:
        # না হলে সাধারণ ওয়েবে সার্চ (Google) করা
        general_results = search_web(query)
        return jsonify({'results': general_results, 'source': 'Google'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
