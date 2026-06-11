from flask import Flask, Response, request
import requests
import os
from urllib.parse import urljoin

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://ycn-redirect.com/",
    "Origin": "https://ycn-redirect.com"
}

@app.route('/stream')
def stream_proxy():
    target_url = request.args.get('url', "https://het4444.ycn-redirect.com/live/lb2/bm1-multi.m3u8")
    
    try:
        r = requests.get(target_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return f"Error: {r.status_code}", r.status_code

        content = r.text
        lines = content.splitlines()
        new_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if not line.startswith('#'):
                full_url = urljoin(target_url, line)
                proxy_url = f"{request.base_url}?url={full_url}"
                new_lines.append(proxy_url)
            else:
                new_lines.append(line)

        modified_manifest = "\n".join(new_lines)
        return Response(modified_manifest, 
                        content_type='application/vnd.apple.mpegurl',
                        headers={"Access-Control-Allow-Origin": "*"})

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
