import os
import requests
from flask import Flask, Response, stream_with_context, render_template_string

app = Flask(__name__)

# تفعيل تصاريح CORS كاملة
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

BASE_URL = "http://atk97.online:80"
MAC_ADDRESS = "00:1A:79:0D:0F:7B"
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
    return "IPTV Proxy Server with Web Player Support is Active!"

# 1. جلب القنوات
@app.route('/playlist.m3u')
def get_playlist():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("mac", MAC_ADDRESS, domain=BASE_URL.split("//")[-1].split(":")[0])
    portal_api = f"{BASE_URL}/c/server/load.php"
    
    try:
        session.get(f"{portal_api}?type=stb&action=handshake&JsHttpRequest=1-xml", timeout=10)
        auth_url = f"{portal_api}?type=stb&action=get_profile&hd=1&sn=0000000000000&stb_type=MAG250&mac={MAC_ADDRESS}&JsHttpRequest=1-xml"
        auth_response = session.get(auth_url, timeout=10).json()
        
        if 'js' in auth_response and 'token' in auth_response['js']:
            session.headers.update({"Authorization": f"Bearer {auth_response['js']['token']}"})
            
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
                    # تحويل صيغة الرابط في الملف ليكون متوافقاً مع مشغلات الويب الحديثة
                    proxy_stream_url = f"{PUBLIC_HOST}/live/{stream_id}.m3u8"
                    m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}", {name}\n{proxy_stream_url}\n'
            
            return Response(m3u_content, mimetype='audio/x-mpegurl')
        else:
            return "No channels found", 500
    except Exception as e:
        return f"Error: {e}", 500

# 2. دفق الفيديو بخدعة صيغة الـ M3U8 للمتصفحات والأندرويد
@app.route('/live/<stream_id>.m3u8')
def stream_channel(stream_id):
    # السيرفر الأصلي يطلب .ts، لكننا نمرره للمستخدم بصيغة m3u8 لخداع المشغل الداخلي
    stream_url = f"{BASE_URL}/play/live.php?mac={MAC_ADDRESS}&stream={stream_id}&extension=ts"
    
    def generate():
        req = requests.get(stream_url, headers=HEADERS, stream=True, timeout=15)
        for chunk in req.iter_content(chunk_size=16384):
            if chunk:
                yield chunk
                
    # إرسال البيانات بنوع Content-Type الخاص بالبث المباشر المعتمد من أندرويد وجميع المتصفحات
    return Response(stream_with_context(generate()), content_type='application/x-mpegURL')

# 3. صفحة مشغل الويب HTML5 المتكاملة والذكية لتطبيقك (تستخدم مكتبة الـ VideoJS العاليمة)
@app.route('/player/<stream_id>')
def player_page(stream_id):
    stream_url = f"{PUBLIC_HOST}/live/{stream_id}.m3u8"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Player</title>
        <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
        <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }
            .video-js { width: 100% !important; height: 100% !important; }
        </style>
    </head>
    <body>
        <video id="my-video" class="video-js vjs-default-skin vjs-big-play-centered" 
               controls preload="auto" autoplay playsinline muted data-setup="{}">
            <source src="{{ stream_url }}" type="application/x-mpegURL">
        </video>
        <script>
            var player = videojs('my-video');
            player.ready(function() {
                player.play();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, stream_url=stream_url)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
