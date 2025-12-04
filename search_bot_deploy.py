from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import random
import re

app = Flask(__name__)

# ==========================================
# 🎨 ফ্রন্টএন্ড ডিজাইন (HTML/CSS/JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced AI Assistant - Sayeef Adnan</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Hind+Siliguri:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f0c29;
            --bg-gradient: linear-gradient(301deg, #0f0c29, #302b63, #24243e);
            --glass-bg: rgba(20, 20, 20, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --accent-color: #00d2ff;
            --text-main: #e0e0e0;
            --bot-bubble: rgba(40, 40, 60, 0.9);
            --user-bubble: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Hind Siliguri', sans-serif;
            background: var(--bg-gradient);
            background-size: 200% 200%;
            animation: gradientBG 15s ease infinite;
            height: 100vh;
            display: flex;
            flex-direction: column;
            color: var(--text-main);
            overflow: hidden;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* --- Header --- */
        .header {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(20px);
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid var(--glass-border);
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
            z-index: 100;
        }

        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(to right, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
        }

        .branding { font-size: 10px; letter-spacing: 2px; color: #888; text-transform: uppercase; margin-top: 5px; }

        /* --- Chat Area --- */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 25px;
            scroll-behavior: smooth;
        }
        .chat-container::-webkit-scrollbar { width: 5px; }
        .chat-container::-webkit-scrollbar-thumb { background: #3a7bd5; border-radius: 10px; }

        .message {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 20px;
            font-size: 15px;
            line-height: 1.7;
            position: relative;
            animation: slideIn 0.4s cubic-bezier(0.25, 1, 0.5, 1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-msg {
            align-self: flex-end;
            background: var(--user-bubble);
            color: #fff;
            border-bottom-right-radius: 2px;
        }

        .bot-msg {
            align-self: flex-start;
            background: var(--bot-bubble);
            border: 1px solid var(--glass-border);
            color: #ddd;
            border-bottom-left-radius: 2px;
        }

        .bot-header {
            font-weight: bold;
            color: var(--accent-color);
            margin-bottom: 10px;
            font-size: 13px;
            border-bottom: 1px dashed rgba(255,255,255,0.1);
            padding-bottom: 5px;
        }

        /* --- Content Styling --- */
        .content-text { margin-bottom: 10px; }
        .extracted-image {
            width: 100%;
            border-radius: 10px;
            margin: 10px 0;
            border: 2px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        .extracted-image:hover { transform: scale(1.02); }

        .cinefreak-section {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #444;
        }
        .cinefreak-header { color: #ff9800; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; gap: 5px; }
        .movie-card {
            background: rgba(255,255,255,0.05);
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 5px;
            font-size: 13px;
        }
        .movie-title { color: #fff; font-weight: 600; }
        .movie-desc { color: #aaa; font-size: 11px; }

        /* --- Buttons --- */
        .feedback-area {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .action-btn {
            padding: 8px 16px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            transition: 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .btn-yes { background: rgba(76, 175, 80, 0.2); color: #4CAF50; border: 1px solid #4CAF50; }
        .btn-yes:hover { background: #4CAF50; color: white; }
        .btn-no { background: rgba(244, 67, 54, 0.2); color: #F44336; border: 1px solid #F44336; }
        .btn-no:hover { background: #F44336; color: white; }

        /* --- Input Area --- */
        .input-area {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(20px);
            padding: 15px;
            display: flex;
            gap: 10px;
            border-top: 1px solid var(--glass-border);
        }
        input {
            flex: 1;
            padding: 15px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 16px;
            outline: none;
        }
        input:focus { border-color: var(--accent-color); box-shadow: 0 0 10px rgba(0, 210, 255, 0.3); }
        button#sendBtn {
            width: 50px; height: 50px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            color: white;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6);
            transition: 0.3s;
        }
        button#sendBtn:hover { transform: scale(1.1); }

        /* --- Loader --- */
        .typing { display: flex; gap: 4px; padding: 5px; }
        .typing span { width: 6px; height: 6px; background: #fff; border-radius: 50%; animation: blink 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0%, 100% { opacity: 0.2; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }

        /* --- Footer --- */
        .footer { text-align: center; padding: 10px; font-size: 11px; background: #000; color: #555; }
        .footer a { color: #777; text-decoration: none; }
    </style>
</head>
<body>

<div class="header">
    <h1>AI Nexus</h1>
    <div class="branding">Build by Sayeef Adnan</div>
</div>

<div class="chat-container" id="chatBox">
    <div class="message bot-msg">
        <div class="bot-header">System Initialized 🟢</div>
        আসসালামু আলাইকুম! আমি <strong>আদনান</strong>-এর তৈরি অ্যাডভান্সড AI। 😎<br>
        আপনার যেকোনো প্রশ্ন করুন, আমি গভীর বিশ্লেষণ করে উত্তর দেব।
    </div>
</div>

<div class="input-area">
    <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off" onkeypress="if(event.key === 'Enter') startSearch()">
    <button onclick="startSearch()" id="sendBtn">➤</button>
</div>

<div class="footer">
    <div>⚠️ Warning: Copying Adnan's website without permission is a punishable offense.</div>
    <div>Developed by <strong>Sayeef Adnan</strong>.</div>
    <div>Contact: <a href="mailto:iamadtul@gmail.com">iamadtul@gmail.com</a></div>
</div>

<script>
    let lastQuery = "";
    let currentResultIndex = 0;

    async function startSearch() {
        const input = document.getElementById('userInput');
        const query = input.value.trim();
        if (!query) return;

        lastQuery = query;
        currentResultIndex = 0; // নতুন সার্চ, তাই ইনডেক্স রিসেট
        
        await processQuery(query, 0);
        input.value = '';
    }

    async function processQuery(query, index) {
        const chatBox = document.getElementById('chatBox');
        
        // User Message (শুধুমাত্র প্রথমবার দেখাব)
        if (index === 0) {
            chatBox.innerHTML += `<div class="message user-msg">${query}</div>`;
        }
        
        chatBox.scrollTop = chatBox.scrollHeight;

        // Loader
        const loadingId = 'loading-' + Date.now();
        chatBox.innerHTML += `<div class="message bot-msg" id="${loadingId}">
            <div class="typing"><span></span><span></span><span></span></div>
        </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query, index: index})
            });
            
            const data = await response.json();
            document.getElementById(loadingId).remove();

            // Adnan Info (Special Case)
            if (data.is_adnan) {
                let html = `<div class="bot-header">Identity Protocol 🆔</div>`;
                html += data.text + "<br><br>😇";
                
                // Signature
                html += `<div style="margin-top:15px; border-top:1px solid #333; padding-top:5px; font-size:11px; color:#666;">
                            Build by Sayeef Adnan | Unauthorized copy prohibited 🚫
                         </div>`;
                         
                chatBox.innerHTML += `<div class="message bot-msg">${html}</div>`;
                return;
            }

            // Normal Content
            let contentHTML = `<div class="bot-header">Analysis Complete 🧠</div>`;
            contentHTML += `<div>আপনার প্রশ্নের জন্য ধন্যবাদ! 😊</div><br>`;
            
            // Text Content from Website
            if (data.content) {
                contentHTML += `<div class="content-text">${data.content}</div>`;
            } else {
                contentHTML += `<div>দুঃখিত, এই বিষয়ে যথেষ্ট তথ্য পাওয়া যায়নি। 😔</div>`;
            }

            // Images
            if (data.images && data.images.length > 0) {
                data.images.forEach(img => {
                    contentHTML += `<img src="${img}" class="extracted-image" onerror="this.style.display='none'">`;
                });
            }

            // CineFreak Section (Always append if available)
            if (data.cinefreak && data.cinefreak.length > 0) {
                contentHTML += `<div class="cinefreak-section">
                    <div class="cinefreak-header">🎬 এসব সম্পর্কে কয়েকটি মুভি:</div>`;
                
                data.cinefreak.forEach(movie => {
                    contentHTML += `<div class="movie-card">
                        <div class="movie-title">${movie.title}</div>
                    </div>`;
                });
                contentHTML += `</div>`;
            }

            // Feedback Buttons
            contentHTML += `<div class="feedback-area" id="feedback-${loadingId}">
                <button class="action-btn btn-yes" onclick="handleYes('${loadingId}')">✅ হ্যাঁ, সন্তুষ্ট</button>
                <button class="action-btn btn-no" onclick="handleNo('${loadingId}')">❌ না, অন্য তথ্য দিন</button>
            </div>`;

            // Signature
            contentHTML += `<div style="margin-top:15px; border-top:1px solid #333; padding-top:5px; font-size:11px; color:#666;">
                            Build by Sayeef Adnan | Unauthorized copy prohibited 🚫
                         </div>`;

            chatBox.innerHTML += `<div class="message bot-msg">${contentHTML}</div>`;
            
            // Save current index for 'No' logic
            currentResultIndex = data.next_index;

        } catch (e) {
            document.getElementById(loadingId)?.remove();
            chatBox.innerHTML += `<div class="message bot-msg">System Error ⚠️ যোগাযোগ: iamadtul@gmail.com</div>`;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function handleYes(id) {
        document.getElementById(`feedback-${id}`).innerHTML = `<div style="color:#4CAF50; font-style:italic;">ধন্যবাদ! অন্য প্রশ্ন করুন... 😊</div>`;
    }

    function handleNo(id) {
        document.getElementById(`feedback-${id}`).innerHTML = `<div style="color:#F44336; font-style:italic;">অন্য সোর্স থেকে তথ্য আনা হচ্ছে... ⏳</div>`;
        processQuery(lastQuery, currentResultIndex);
    }

</script>
</body>
</html>
"""

# ==========================================
# ⚙️ ব্যাকএন্ড লজিক (AI & Scraper Core)
# ==========================================

def get_duckduckgo_links(query):
    """DuckDuckGo থেকে সার্চ রেজাল্ট লিংক আনে (Google ব্লক এড়াতে)"""
    url = "https://html.duckduckgo.com/html/"
    payload = {'q': query}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = []
        for a in soup.find_all('a', class_='result__a'):
            href = a['href']
            # DuckDuckGo রিডাইরেক্ট লিংক ডিকোড করা
            if 'duckduckgo.com/l/?uddg=' in href:
                href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
            links.append(href)
        return links
    except:
        return []

def scrape_website_content(url):
    """লিংকের ভেতর থেকে শুধু টেক্সট এবং ছবি বের করে আনে (লিংক ছাড়া)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200: return None, None
        
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # স্ক্রিপ্ট ও স্টাইল রিমুভ
        for s in soup(['script', 'style', 'nav', 'footer', 'header']):
            s.decompose()
            
        # টেক্সট এক্সট্রাকশন (প্যারাগ্রাফ)
        paragraphs = soup.find_all('p')
        text_content = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50: # ছোট লাইন বাদ
                text_content += f"<p>{text}</p>"
            if len(text_content) > 1500: break # খুব বেশি বড় টেক্সট না নেওয়া
            
        # ইমেজ এক্সট্রাকশন
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src.startswith('http'):
                # ছোট আইকন বাদ দেওয়া
                if 'icon' not in src and 'logo' not in src:
                    images.append(src)
            if len(images) >= 2: break # সর্বোচ্চ ২টি ছবি
            
        return text_content, images
    except:
        return None, None

def search_cinefreak(query):
    """CineFreak থেকে মুভি সাজেশন আনে"""
    url = f"https://www.cinefreak.net/?s={urllib.parse.quote_plus(query)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        movies = []
        
        articles = soup.find_all('article')
        if not articles: articles = soup.find_all('div', class_='post')
        
        for post in articles:
            title = post.find('h2') or post.find('h1')
            if title:
                movies.append({'title': title.get_text().strip()})
            if len(movies) >= 3: break
        return movies
    except:
        return []

# --- API Route ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_api():
    data = request.json
    query = data.get('query', '')
    start_index = data.get('index', 0)
    
    # ১. আদনান স্পেশাল চেক
    if 'আদনান' in query or 'adnan' in query.lower():
        adnan_info = """
        আদনান একজন খুব ভালো ছেলে 😊।<br>
        তার সম্পর্কে সে বেশি কিছু তথ্য দিতে নিষেধ করেছে।<br>
        তবে জেনে রাখুন, আমাকে (এই AI-কে) সেই বানিয়েছে আল্লাহর রহমতে। ❤️<br>
        সে প্রযুক্তি ভালোবাসে এবং মানুষের উপকারে কাজ করতে পছন্দ করে।
        """
        return jsonify({'is_adnan': True, 'text': adnan_info})

    # ২. ওয়েব সার্চ (DuckDuckGo)
    search_links = get_duckduckgo_links(query)
    
    final_content = None
    final_images = []
    next_index = start_index + 1
    
    # লুপ চালিয়ে একটার পর একটা সাইট চেক করা (start_index থেকে শুরু)
    for i in range(start_index, len(search_links)):
        url = search_links[i]
        text, imgs = scrape_website_content(url)
        
        if text: # যদি সফলভাবে টেক্সট পাওয়া যায়
            final_content = text
            final_images = imgs
            next_index = i + 1 # পরের বার এখান থেকে শুরু হবে
            break
            
    # ৩. CineFreak ডাটা (সব সময় ব্যাকআপ হিসেবে থাকবে)
    cinefreak_data = search_cinefreak(query)

    return jsonify({
        'is_adnan': False,
        'content': final_content,
        'images': final_images,
        'cinefreak': cinefreak_data,
        'next_index': next_index
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



