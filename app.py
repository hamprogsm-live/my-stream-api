import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, make_response

app = Flask(__name__)

# قاموس ذكي لتحويل أسماء المنتخبات والأندية إلى أعلام إيموجي تلقائياً
FLAG_MAPPING = {
    "فرنسا": "🇫🇷", "السنغال": "🇸🇳", "العراق": "🇮🇶", "النرويج": "🇳🇴",
    "الأرجنتين": "🇦🇷", "الجزائر": "🇩🇿", "النمسا": "🇦🇹", "الأردن": "🇯🇴",
    "البرتغال": "🇵🇹", "الكونغو الديمقراطية": "🇨🇩", "إنجلترا": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "كرواتيا": "🇭🇷",
    "غانا": "🇬🇭", "بنما": "🇵🇦", "أوزبكستان": "🇺🇿", "كولومبيا": "🇨🇴",
    "إسبانيا": "🇪🇸", "الرأس الأخضر": "🇨🇻", "بلجيكا": "🇧🇪", "مصر": "🇪🇬",
    "السعودية": "🇸🇦", "أوروغواي": "🇺🇾", "إيران": "🇮🇷", "نيوزيلندا": "🇳🇿", "تونس": "🇹🇳",
    "المغرب": "🇲🇦", "الإمارات": "🇦🇪", "قطر": "🇶🇦", "البرازيل": "🇧🇷", "إيطاليا": "🇮🇹"
}

def get_live_matches():
    """كشط بيانات المباريات بشكل حي وتلقائي من موقع كورة سيمو"""
    url = "https://www.korasimo.com/simokora"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    matches = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            match_rows = soup.find_all('a', class_='match-row')
            
            for row in match_rows:
                try:
                    # استخراج أسماء الفرق
                    teams = row.find_all('div', class_='team')
                    home_team = teams[0].find('div', class_='team-name').text.strip()
                    away_team = teams[1].find('div', class_='team-name').text.strip()
                    
                    # تحديد الأعلام من القاموس أو وضع علم افتراضي إذا لم يتوفر
                    home_flag = FLAG_MAPPING.get(home_team, "⚽")
                    away_flag = FLAG_MAPPING.get(away_team, "⚽")
                    
                    # استخراج الوقت أو النتيجة والبطولة
                    center_div = row.find('div', class_='center')
                    score_time = center_div.find('div', class_='score-time').text.strip()
                    
                    status_badge = center_div.find('div', class_='status-badge')
                    status_text = status_badge.text.strip() if status_badge else "لم تبدأ"
                    
                    league = center_div.find('div', class_='league').text.strip() if center_div.find('div', class_='league') else "بطولة دولية"
                    
                    # تحديد حالة المباراة للتصميم
                    is_finished = "انتهت" in status_text or "ended" in status_text.lower()
                    
                    matches.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_flag": home_flag,
                        "away_flag": away_flag,
                        "time": score_time,
                        "status": "finished" if is_finished else "time",
                        "status_text": status_text,
                        "competition": league,
                        "commentator": "بث مباشر حـي",
                        "channel": "بث حصري"
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error scraping data: {e}")
        
    # إذا فشل الجلب أو كانت القائمة فارغة، نضع بيانات احتياطية لكي لا تظهر صفحة بيضاء
    if not matches:
        matches = [
            {
                "status": "time", "time": "20:00", "status_text": "قريباً",
                "home_team": "فرنسا", "away_team": "السنغال", "home_flag": "🇫🇷", "away_flag": "🇸🇳",
                "competition": "كأس العالم - الجولة 1", "commentator": "بث مباشر حـي", "channel": "beIN MAX 1"
            },
            {
                "status": "time", "time": "23:00", "status_text": "لم تبدأ بعد",
                "home_team": "العراق", "away_team": "النرويج", "home_flag": "🇮🇶", "away_flag": "🇳🇴",
                "competition": "كأس العالم - الجولة 1", "commentator": "بث مباشر حـي", "channel": "beIN MAX 2"
            }
        ]
    return matches

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
        .team-name { color: #B80000; font-size: 16px; font-weight: 700; margin-top: 8px; }
        
        .flag {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #fdfdfd;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            border: 1px solid #eee;
        }
        
        .center-info { display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 120px; }
        
        .score-time {
            font-size: 18px;
            font-weight: bold;
            color: #111827;
            direction: ltr;
            margin-bottom: 4px;
        }
        
        .status-badge {
            background-color: #EEEEEE;
            color: #333333;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-align: center;
        }
        
        .finished { background-color: #D31515; color: white; }
        
        .match-info { width: 100%; border-top: 1px dashed #E8E8E8; padding-top: 12px; text-align: center; }
        .competition { color: #555555; font-size: 13px; font-weight: bold; margin-bottom: 6px; }
        .meta-data { display: flex; justify-content: space-around; color: #777777; font-size: 12px; }
    </style>
</head>
<body>

    <div class="top-bar">جدول مباريات اليوم</div>

    <div class="container">
        {% for match in matches %}
        <div class="match-card">
            <div class="teams-row">
                <!-- الفريق 1 -->
                <div class="team">
                    <div class="flag">{{ match.home_flag }}</div>
                    <div class="team-name">{{ match.home_team }}</div>
                </div>
                
                <!-- الوقت والوضع -->
                <div class="center-info">
                    <div class="score-time">{{ match.time }}</div>
                    <div class="status-badge {% if match.status == 'finished' %}finished{% endif %}">
                        {{ match.status_text }}
                    </div>
                </div>
                
                <!-- الفريق 2 -->
                <div class="team">
                    <div class="flag">{{ match.away_flag }}</div>
                    <div class="team-name">{{ match.away_team }}</div>
                </div>
            </div>
            
            <div class="match-info">
                <div class="competition">🏆 {{ match.competition }}</div>
                <div class="meta-data">
                    <div>🎙️ {{ match.commentator }}</div>
                    <div>📺 {{ match.channel }}</div>
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
    rendered_html = render_template_string(HTML_TEMPLATE, matches=matches)
    response = make_response(rendered_html)
    
    # فك الحظر لتشغيله في أي مكان بأمان
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = "frame-ancestors *;"
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
