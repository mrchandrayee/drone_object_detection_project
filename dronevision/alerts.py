import os,time,requests
class TelegramAlerter:
    def __init__(self,cfg):
        self.enabled=cfg.get("enabled",False); self.send_photo_enabled=cfg.get("send_photo",True)
        self.token=os.getenv("TELEGRAM_BOT_TOKEN"); self.chat_id=os.getenv("TELEGRAM_CHAT_ID")
        self.cooldown=cfg.get("alert_cooldown_seconds",30); self.last={}
    def send(self,message,photo=None):
        if not self.enabled or not self.token or not self.chat_id: return
        now=time.time()
        if now-self.last.get(message,0)<self.cooldown: return
        base=f"https://api.telegram.org/bot{self.token}/"
        try:
            if photo and self.send_photo_enabled:
                with open(photo,"rb") as f:
                    requests.post(base+"sendPhoto",data={"chat_id":self.chat_id,"caption":message},files={"photo":f},timeout=20).raise_for_status()
            else: requests.post(base+"sendMessage",data={"chat_id":self.chat_id,"text":message},timeout=20).raise_for_status()
            self.last[message]=now
        except requests.RequestException as e: print("[telegram]",e)
