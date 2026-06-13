import os
import requests
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

# تفعيل تصاريح CORS كاملة لإزالة قيود الأندرويد
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

BASE_URL = "http://bolachas.live:80"
MAC_ADDRESS = "00:1A:79:c3:de:a5"
USER_AGENT_MAG = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 sb_api_version=6 EmbeddedLinux Tasman IPTV navigator"

PUBLIC_HOST = "https://my-stream-api-production.up.railway.app"

HEADERS = {
    "User-Agent": USER_AGENT_MAG,
    "X-User-Agent": "model=MAG250;link=ethernet",
    "Referer": f"{BASE_URL}/c/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive"
}

@app.route('/')
def home():
    return "Bolachas Proxy for AppCreator24 Internal Player is Active!"

# 1. جلب قائمة القنوات وتحويل امتداداتها إلى m3u8 لخداع التطبيق
@app.route('/playlist.m3u')
def get_playlist():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("mac", MAC_ADDRESS, domain=BASE_URL.split("//")[-1].split(":")[0])
    portal_api = f"{BASE_URL}/c/server/load.php"
    
    try:
        session.get(f"{portal_api}?type=stb&action=handshake&JsHttpRequest=1-xml", timeout=12)
        auth_url = f"{portal_api}?type=stb&action=get_profile&hd=1&sn=0000000000000&stb_type=MAG250&mac={MAC_ADDRESS}&JsHttpRequest=1-xml"
        auth_response = session.get(auth_url, timeout=12).json()
        
        if 'js' in auth_response and 'token' in auth_response['js']:
            session.headers.update({"Authorization": f"Bearer {auth_response['js']['token']}"})
            
        channels_url = f"{portal_api}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
        channels_data = session.get(channels_url, timeout=30).json()
        
        if 'js' in channels_data and 'data' in channels_data['js']:
            m3u_content = "#EXTM3U\n"
            for ch in channels_data['js']['data']:
                name = ch.get('name', 'Unknown')
                cmd = ch.get('cmd', '')
                ch_id = ch.get('id', '')
                
                stream_id = ""
                if "stream=" in cmd:
                    stream_id = cmd.split("stream=")[1].split("&")[0]
                    
                if stream_id:
                    # غيرنا الامتداد هنا إلى .m3u8 لإقناع مشغل AppCreator24 بالدخول للقناة
                    proxy_stream_url = f"{PUBLIC_HOST}/live/{stream_id}.m3u8"
                    m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}", {name}\n{proxy_stream_url}\n'
            
            return Response(m3u_content, mimetype='audio/x-mpegurl')
        else:
            return "No channels found", 500
    except Exception as e:
        return f"Error: {e}", 500

# 2. استقبال طلب الـ m3u8 وتمرير داتا الـ ts الحقيقية بنوع هيدر متوافق مع أندرويد
@app.route('/live/<stream_id>.m3u8')
def stream_channel(stream_id):
    stream_url = f"{BASE_URL}/play/live.php?mac={MAC_ADDRESS}&stream={stream_id}&extension=ts"
    
    def generate():
        req = requests.get(stream_url, headers=HEADERS, stream=True, timeout=20)
        for chunk in req.iter_content(chunk_size=32768): # حجم دفق كبير لثبات البث الداخلي
            if chunk:
                yield chunk
                
    # الخدعة هنا: نرسل داتا الـ ts ولكن بهيدر ترفيهي ونوع ميما يقرأه مشغل التطبيق على أنه HLS
    return Response(stream_with_context(generate()), content_type='application/x-mpegURL')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
