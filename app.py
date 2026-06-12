import os
import requests
from flask import Flask, Response, stream_with_context, redirect

app = Flask(__name__)

BASE_URL = "http://atk97.online:80"
MAC_ADDRESS = "00:1A:79:0D:0F:7B"
USER_AGENT_MAG = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 sb_api_version=6 EmbeddedLinux Tasman IPTV navigator"

# الدومين العام والثابت الخاص بك على Railway
PUBLIC_HOST = "https://my-stream-api-production.up.railway.app"

HEADERS = {
    "User-Agent": USER_AGENT_MAG,
    "X-User-Agent": "model=MAG250;link=ethernet",
    "Referer": f"{BASE_URL}/c/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive"
}

# الصفحة الرئيسية للتأكد من عمل البروكسي بنجاح
@app.route('/')
def home():
    return "IPTV Proxy Server is Running Successfully! Use /playlist.m3u to fetch channels."

# 1. رابط جلب ملف القنوات الكامل (M3U Playlist)
@app.route('/playlist.m3u')
def get_playlist():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("mac", MAC_ADDRESS, domain=BASE_URL.split("//")[-1].split(":")[0])
    portal_api = f"{BASE_URL}/c/server/load.php"
    
    try:
        # عمل الـ Handshake الأولي لتوليد الجلسة
        session.get(f"{portal_api}?type=stb&action=handshake&JsHttpRequest=1-xml", timeout=10)
        auth_url = f"{portal_api}?type=stb&action=get_profile&hd=1&sn=0000000000000&stb_type=MAG250&mac={MAC_ADDRESS}&JsHttpRequest=1-xml"
        auth_response = session.get(auth_url, timeout=10).json()
        
        if 'js' in auth_response and 'token' in auth_response['js']:
            session.headers.update({"Authorization": f"Bearer {auth_response['js']['token']}"})
            
        # سحب الـ 49 ألف قناة بالكامل
        channels_url = f"{portal_api}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
        channels_data = session.get(channels_url, timeout=25).json()
        
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
                    # توجيه الروابط إلى سيرفر Railway الخاص بك
                    proxy_stream_url = f"{PUBLIC_HOST}/live/{stream_id}.ts"
                    m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}", {name}\n{proxy_stream_url}\n'
            
            return Response(m3u_content, mimetype='audio/x-mpegurl')
        else:
            return "No channels found from the server response.", 500
    except Exception as e:
        return f"Error generating playlist: {e}", 500

# 2. رابط البث المطور بنظام الـ Redirect لمنع الانقطاع نهائياً
@app.route('/live/<stream_id>.ts')
def stream_channel(stream_id):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("mac", MAC_ADDRESS, domain=BASE_URL.split("//")[-1].split(":")[0])
    portal_api = f"{BASE_URL}/c/server/load.php"
    
    try:
        # تجديد تسجيل الدخول وجلب Token جديد مخصص لهذه القناة بسرعة فائقة لمنع الحظر
        session.get(f"{portal_api}?type=stb&action=handshake&JsHttpRequest=1-xml", timeout=5)
        auth_url = f"{portal_api}?type=stb&action=get_profile&hd=1&sn=0000000000000&stb_type=MAG250&mac={MAC_ADDRESS}&JsHttpRequest=1-xml"
        session.get(auth_url, timeout=5)
        
        # رابط البث النهائي المباشر من السيرفر الأصلي
        stream_url = f"{BASE_URL}/play/live.php?mac={MAC_ADDRESS}&stream={stream_id}&extension=ts"
        
        # عمل تحويل مباشر (302 Redirect) للمشغل ليتصل بالسيرفر مباشرة بدون وسيط يسبب بطء
        return redirect(stream_url)
        
    except Exception as e:
        return f"Stream initialization failed: {e}", 500

if __name__ == '__main__':
    # جلب منفذ التشغيل تلقائياً من إعدادات المنصة
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
