import os
from flask import Flask, render_template_string, make_response

app = Flask(__name__)

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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
