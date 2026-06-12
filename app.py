import requests

BASE_URL = "http://atk97.online:80"
MAC_ADDRESS = "00:1A:79:0D:0F:7B"

# الهوية المطلوبة لتخطي حماية السيرفر
USER_AGENT_MAG = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 sb_api_version=6 EmbeddedLinux Tasman IPTV navigator"

HEADERS = {
    "User-Agent": USER_AGENT_MAG,
    "X-User-Agent": "model=MAG250;link=ethernet",
    "Referer": f"{BASE_URL}/c/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive"
}

def fetch_stalker_to_vlc():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("mac", MAC_ADDRESS, domain=BASE_URL.split("//")[-1].split(":")[0])
    
    portal_api = f"{BASE_URL}/c/server/load.php"
    
    print("[*] جاري عمل Handshake وتخطي الحماية...")
    try:
        # 1. الـ Handshake الأولي
        session.get(f"{portal_api}?type=stb&action=handshake&JsHttpRequest=1-xml", timeout=10)
        
        # 2. تسجيل الدخول وتوليد الجلسة
        auth_url = f"{portal_api}?type=stb&action=get_profile&hd=1&sn=0000000000000&stb_type=MAG250&mac={MAC_ADDRESS}&JsHttpRequest=1-xml"
        auth_response = session.get(auth_url, timeout=10)
        auth_data = auth_response.json()
        
        if 'js' in auth_data and 'token' in auth_data['js']:
            token = auth_data['js']['token']
            session.headers.update({"Authorization": f"Bearer {token}"})
            print("[+] تم تسجيل الدخول بنجاح.")
            
        # 3. جلب القنوات
        print("[*] جاري سحب قائمة القنوات حالياً البالغة 49 ألف قناة...")
        channels_url = f"{portal_api}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
        channels_response = session.get(channels_url, timeout=20)
        channels_data = channels_response.json()
        
        if 'js' in channels_data and 'data' in channels_data['js']:
            channels_list = channels_data['js']['data']
            print(f"[+] تم جلب {len(channels_list)} قناة بنجاح. جاري التعديل لصيغة VLC المباشرة...")
            
            # 4. حفظ ملف M3U مخصص ومتوافق مع VLC مباشرة
            with open("channels.m3u", "w", encoding="utf-8") as file:
                file.write("#EXTM3U\n")
                
                for ch in channels_list:
                    name = ch.get('name', 'Unknown')
                    cmd = ch.get('cmd', '')
                    ch_id = ch.get('id', '')
                    
                    # تنظيف واستخراج معرف القناة (Stream ID) من الرابط الداخلي للسيرفر
                    # الروابط الداخلية تكون غالباً مثل: ffmpeg http://.../play/live.php?mac=...&stream=123
                    stream_id = ""
                    if "stream=" in cmd:
                        try:
                            stream_id = cmd.split("stream=")[1].split("&")[0]
                        except IndexError:
                            pass
                    
                    if not stream_id:
                        continue # تخطي القناة إذا لم نجد المعرف الخاص بها
                        
                    # تركيب رابط البث المباشر النهائي الصالح للتشغيل الخارجي
                    stream_url = f"{BASE_URL}/play/live.php?mac={MAC_ADDRESS}&stream={stream_id}&extension=ts"
                    
                    # سطر السحر لـ VLC: يخبر البرنامج باستخدام الـ User-Agent الصحيح تلقائياً عند فتح القناة
                    file.write(f'#EXTINF:-1 tvg-id="{ch_id}", {name}\n')
                    file.write(f'#EXTVLCOPT:http-user-agent={USER_AGENT_MAG}\n')
                    file.write(f'{stream_url}\n')
                    
            print("[+] مبروك! تم حفظ القنوات الجاهزة لـ VLC في ملف: channels.m3u")
        else:
            print("[-] لم يتم العثور على القنوات. تأكد من أن السيرفر مستقر.")
            
    except Exception as e:
        print(f"[-] حدث خطأ أثناء المعالجة: {e}")

if __name__ == "__main__":
    fetch_stalker_to_vlc()
