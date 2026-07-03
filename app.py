import os
import time
import requests
from datetime import datetime
from flask import Flask, render_template_string, make_response, jsonify, request

app = Flask(__name__)

# ==============================
# إعدادات API-FOOTBALL
# ==============================
# يفضل وضع المفتاح كمتغير بيئة (Environment Variable) باسم API_FOOTBALL_KEY
# بدلاً من كتابته مباشرة في الكود، لكن تم توفير قيمة افتراضية هنا للتجربة السريعة.
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "e443b3250a452e23de6a392ea2b22d75")
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"

# البطولات الكبرى فقط (يمكنك إضافة/حذف حسب رغبتك)
# مصدر المعرفات: https://www.api-football.com/documentation-v3#tag/Leagues
MAJOR_LEAGUES = {
    1: "كأس العالم",
    2: "دوري أبطال أوروبا",
    3: "الدوري الأوروبي",
    39: "الدوري الإنجليزي الممتاز",
    140: "الدوري الإسباني",
    135: "الدوري الإيطالي",
    78: "الدوري الألماني",
    61: "الدوري الفرنسي",
    45: "كأس الاتحاد الإنجليزي",
    848: "دوري المؤتمر الأوروبي",
}

# ==============================
# كاش بسيط في الذاكرة (In-memory cache)
# ==============================
_matches_cache = {"data": None, "timestamp": 0}
CACHE_TTL_SECONDS = 300  # 5 دقائق


def fetch_today_major_matches():
    """يجلب كل مباريات اليوم من API-FOOTBALL ثم يفلتر على البطولات الكبرى فقط."""
    today = datetime.now().strftime("%Y-%m-%d")

    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    resp = requests.get(
        f"{API_FOOTBALL_BASE_URL}/fixtures",
        headers=headers,
        params={"date": today},
        timeout=10,
    )
    resp.raise_for_status()
    payload = resp.json()

    matches = []
    for fixture in payload.get("response", []):
        league_id = fixture["league"]["id"]
        if league_id not in MAJOR_LEAGUES:
            continue

        status = fixture["fixture"]["status"]
        matches.append({
            "id": fixture["fixture"]["id"],
            "date": fixture["fixture"]["date"],
            "timestamp": fixture["fixture"]["timestamp"],
            "status_short": status["short"],       # e.g. NS, 1H, HT, FT, LIVE
            "status_long": status["long"],
            "elapsed": status["elapsed"],
            "home_team": fixture["teams"]["home"]["name"],
            "away_team": fixture["teams"]["away"]["name"],
            "home_logo": fixture["teams"]["home"]["logo"],
            "away_logo": fixture["teams"]["away"]["logo"],
            "home_score": fixture["goals"]["home"],
            "away_score": fixture["goals"]["away"],
            "league_id": league_id,
            "league_name": MAJOR_LEAGUES[league_id],
            "league_logo": fixture["league"]["logo"],
            "round": fixture["league"]["round"],
        })

    # ترتيب حسب التوقيت
    matches.sort(key=lambda m: m["timestamp"])
    return matches

# بيانات المباريات مطابقة تماماً للصور التي رفعتها
MATCHES_DATA = [
    {
        "status": "time", "time": "08:00 PM",
        "home_team": "فرنسا", "away_team": "السنغال",
        "home_flag": "🇫🇷", "away_flag": "🇸🇳",
        "competition": "كأس العالم", "commentator": "حسن العيدروس", "channel": "beIN MAX 1"
    },
    {
        "status": "time", "time": "11:00 PM",
        "home_team": "العراق", "away_team": "النرويج",
        "home_flag": "🇮🇶", "away_flag": "🇳🇴",
        "competition": "كأس العالم", "commentator": "عصام الشوالي", "channel": "beIN MAX 2"
    },
    {
        "status": "time", "time": "02:00 AM",
        "home_team": "الأرجنتين", "away_team": "الجزائر",
        "home_flag": "🇦🇷", "away_flag": "🇩🇿",
        "competition": "كأس العالم", "commentator": "حفيظ دراجي", "channel": "beIN MAX 1"
    },
    {
        "status": "time", "time": "05:00 AM",
        "home_team": "النمسا", "away_team": "الأردن",
        "home_flag": "🇦🇹", "away_flag": "🇯🇴",
        "competition": "كأس العالم", "commentator": "خليل البلوشي", "channel": "beIN MAX 2"
    },
    {
        "status": "finished", "time": "إنتهت المباراة",
        "home_team": "إيران", "away_team": "نيو زيلندا",
        "home_flag": "🇮🇷", "away_flag": "🇳🇿",
        "competition": "كأس العالم", "commentator": "عامر الخوذيري", "channel": "beIN MAX 2"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LIVE EVENT</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #f4f4f4; padding-bottom: 30px; -webkit-user-select: none; user-select: none; }
        
        /* البار العلوي الأحمر */
        .top-bar {
            background-color: #D31515;
            color: white;
            text-align: center;
            padding: 20px 0;
            font-size: 22px;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .container { max-width: 550px; margin: 0 auto; padding: 15px; }
        
        /* الكروت */
        .match-card {
            background: #FFFFFF;
            border: 1.5px solid #E8E8E8;
            border-radius: 14px;
            margin-bottom: 18px;
            padding: 18px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .teams-row {
            display: flex;
            width: 100%;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .team { flex: 1; text-align: center; }
        
        .team-name { color: #B80000; font-size: 18px; font-weight: 700; margin-top: 8px; }
        
        /* الأعلام الدائرية الذكية */
        .flag {
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: #fdfdfd;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 35px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            border: 1px solid #eee;
        }
        
        /* التوقيت */
        .match-time {
            background-color: #EEEEEE;
            color: #333333;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 15px;
            font-weight: bold;
            min-width: 115px;
            text-align: center;
            direction: ltr;
        }
        
        .finished { color: #D31515; font-size: 14px; font-weight: bold; direction: rtl; }
        
        /* التفاصيل السفلى */
        .match-info { width: 100%; border-top: 1px dashed #E8E8E8; padding-top: 12px; text-align: center; }
        
        .competition { color: #555555; font-size: 14px; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; gap: 5px; }
        
        .meta-data { display: flex; justify-content: space-around; color: #777777; font-size: 13px; }
        
        .meta-item { display: flex; align-items: center; gap: 5px; }
    </style>
</head>
<body>

    <div class="top-bar">LIVE EVENT</div>

    <div class="container">
        {% for match in matches %}
        <div class="match-card">
            <div class="teams-row">
                <div class="team">
                    <div class="flag">{{ match.home_flag }}</div>
                    <div class="team-name">{{ match.home_team }}</div>
                </div>
                
                <div class="match-time {% if match.status == 'finished' %}finished{% endif %}">
                    {{ match.time }}
                </div>
                
                <div class="team">
                    <div class="flag">{{ match.away_flag }}</div>
                    <div class="team-name">{{ match.away_team }}</div>
                </div>
            </div>
            
            <div class="match-info">
                <div class="competition">🏆 {{ match.competition }}</div>
                <div class="meta-data">
                    <div class="meta-item">🎙️ {{ match.commentator }}</div>
                    <div class="meta-item">📺 {{ match.channel }}</div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

</body>
</html>
"""

@app.route('/')
def index():
    rendered_html = render_template_string(HTML_TEMPLATE, matches=MATCHES_DATA)
    response = make_response(rendered_html)
    
    # فك الحظر تماماً ليعمل الـ iframe في تطبيقك ومحرر الأكواد
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *;"
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response


@app.route('/api/matches')
def api_matches():
    """
    يرجع مباريات اليوم للبطولات الكبرى فقط (كأس العالم، أبطال أوروبا، الدوريات الكبرى...).
    نتائج مخزنة مؤقتاً (كاش) لمدة CACHE_TTL_SECONDS لتقليل عدد الطلبات على API-FOOTBALL.
    استخدم ?refresh=1 لإجبار تحديث الكاش.
    """
    now = time.time()
    force_refresh = request.args.get("refresh") == "1"
    cache_is_fresh = (
        _matches_cache["data"] is not None
        and (now - _matches_cache["timestamp"]) < CACHE_TTL_SECONDS
    )

    if not force_refresh and cache_is_fresh:
        return jsonify({
            "success": True,
            "cached": True,
            "cached_at": _matches_cache["timestamp"],
            "count": len(_matches_cache["data"]),
            "matches": _matches_cache["data"],
        })

    try:
        matches = fetch_today_major_matches()
        _matches_cache["data"] = matches
        _matches_cache["timestamp"] = now
        return jsonify({
            "success": True,
            "cached": False,
            "cached_at": now,
            "count": len(matches),
            "matches": matches,
        })
    except requests.exceptions.RequestException as e:
        # في حال فشل الطلب، أرجع آخر بيانات مخزنة إن وجدت بدل الفشل الكامل
        if _matches_cache["data"] is not None:
            return jsonify({
                "success": True,
                "cached": True,
                "stale": True,
                "error": str(e),
                "cached_at": _matches_cache["timestamp"],
                "count": len(_matches_cache["data"]),
                "matches": _matches_cache["data"],
            })
        return jsonify({
            "success": False,
            "error": str(e),
            "matches": [],
        }), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
