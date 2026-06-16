import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string

app = Flask(__name__)

def get_live_matches():
    """جلب بيانات المباريات الحية من موقع الوان سبورت"""
    matches = []
    try:
        url = "https://www.alwansport.com/matches-today"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ملاحظة: يتم تعديل الكلاسات أدناه بناءً على الهيكل الدقيق لموقع الوان سبورت
            match_elements = soup.find_all(class_='match-card') 
            
            for elem in match_elements:
                home_team = elem.find(class_='home-team').text.strip()
                away_team = elem.find(class_='away-team').text.strip()
                match_time = elem.find(class_='match-time').text.strip()
                
                matches.append({
                    "status": "time",
                    "time": match_time,
                    "home_team": home_team,
                    "away_team": away_team,
                    "competition": "كأس العالم",
                    "commentator": "عصام الشوالي",
                    "channel": "beIN MAX 1"
                })
    except Exception as e:
        print(f"Error scraping data: {e}")
    
    # بيانات احتياطية (تظهر في حال كان الموقع متوقفاً أو فارغاً)
    if not matches:
        matches = [
            {
                "status": "time", "time": "08:00 PM",
                "home_team": "فرنسا", "away_team": "السنغال",
                "competition": "كأس العالم", "commentator": "حسن العيدروس", "channel": "beIN MAX 1"
            },
            {
                "status": "time", "time": "11:00 PM",
                "home_team": "العراق", "away_team": "النرويج",
                "competition": "كأس العالم", "commentator": "عصام الشوالي", "channel": "beIN MAX 2"
            },
            {
                "status": "finished", "time": "إنتهت المباراة",
                "home_team": "إيران", "away_team": "نيو زيلندا",
                "competition": "كأس العالم", "commentator": "عامر الخوذيري", "channel": "beIN MAX 2"
            }
        ]
    return matches

# قالب HTML مدمج ومصمم خصيصاً للهواتف بنظام الـ Cards الشبيه بتطبيقك
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Event</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }
        body {
            background-color: #F8F8F8;
            padding-bottom: 20px;
        }
        /* البار العلوي الثابت */
        .top-bar {
            background-color: #D31515;
            color: white;
            text-align: center;
            padding: 20px 0;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 1px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        /* حاوي الكروت */
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 15px;
        }
        /* كارت المباراة */
        .match-card {
            background: #FFFFFF;
            border: 2px solid #E8E8E8;
            border-radius: 12px;
            margin-bottom: 20px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        /* صف الفريقين والوقت */
        .teams-row {
            display: flex;
            width: 100%;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .team {
            flex: 1;
            text-align: center;
        }
        .team-name {
            color: #B80000;
            font-size: 18px;
            font-weight: 700;
            margin-top: 8px;
        }
        /* الأعلام الافتراضية بشكل دائري جذاب */
        .flag-placeholder {
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: #f0f0f0;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* توقيت المباراة في المنتصف */
        .match-time {
            background-color: #EEEEEE;
            color: #333333;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 15px;
            font-weight: bold;
            min-width: 110px;
            text-align: center;
            direction: ltr;
        }
        .finished {
            color: #D31515;
            font-size: 14px;
        }
        /* تفاصيل أسفل الكارت */
        .match-info {
            width: 100%;
            border-top: 1px dashed #E8E8E8;
            padding-top: 12px;
            text-align: center;
        }
        .competition {
            color: #333333;
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .meta-data {
            display: flex;
            justify-content: space-around;
            color: #666666;
            font-size: 13px;
        }
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
    </style>
</head>
<body>

    <div class="top-bar">LIVE EVENT</div>

    <div class="container">
        {% for match in matches %}
        <div class="match-card">
            <div class="teams-row">
                <div class="team">
                    <div class="flag-placeholder">🏳️</div>
                    <div class="team-name">{{ match.home_team }}</div>
                </div>
                
                <div class="match-time {% if match.status == 'finished' %}finished{% endif %}">
                    {{ match.time }}
                </div>
                
                <div class="team">
                    <div class="flag-placeholder">🏴</div>
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
    matches = get_live_matches()
    return render_template_string(HTML_TEMPLATE, matches=matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
