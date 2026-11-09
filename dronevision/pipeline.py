import time, cv2, numpy as np
from .detector import Detector
from .events import EventStore
from .monitors import ZoneMonitor,RailwayStallMonitor,FallHeuristic
from .geometry import denormalize_polygon
from .alerts import TelegramAlerter
class DroneVisionPipeline:
    def __init__(self,cfg,frame_size):
        self.cfg=cfg; w,h=frame_size
        self.detector=Detector(cfg["model"],cfg.get("confidence",.35),cfg.get("iou",.5),cfg.get("image_size",640),cfg.get("device","auto"),cfg.get("classes"))
        self.store=EventStore(cfg.get("output","runs")); self.camera=cfg.get("camera",{}).get("id","camera")
        self.features=set(cfg.get("features",[])); z=cfg.get("zone",{})
        zp=denormalize_polygon(z.get("polygon",[]),w,h)
        self.zone=ZoneMonitor(zp,z.get("anchor","bottom"),z.get("grace_frames",2)) if "zone_intrusion" in self.features else None
        r=cfg.get("railway",{}); rp=denormalize_polygon(r.get("polygon",[]),w,h)
        self.rail=RailwayStallMonitor(rp,r.get("classes",["train"]),r.get("stall_seconds",5),r.get("min_motion_px",2)) if "railway_stall" in self.features else None
        self.fall=FallHeuristic(cfg.get("fall",{}).get("min_frames",5)) if "fall_detection" in self.features else None
        self.fire_detector=None
        self.fire_cfg=cfg.get("fire",{})
        if "fire_smoke" in self.features:
            fire_model=self.fire_cfg.get("model")
            if not fire_model: raise ValueError("Set fire.model to a trained fire/smoke detector weights file")
            self.fire_detector=Detector(fire_model,cfg.get("confidence",.35),cfg.get("iou",.5),
                                        cfg.get("image_size",640),cfg.get("device","auto"))
        self.alerter=TelegramAlerter(cfg.get("telegram",{})); self.cooldown=cfg.get("events",{}).get("cooldown_seconds",30); self.last={}
    def _record(self,frame,kind,d):
        key=(kind,d["id"]); now=time.time()
        if now-self.last.get(key,0)<self.cooldown: return
        self.last[key]=now; path=self.store.add(frame,self.camera,kind,d["id"],d["label"])
        msg=f"{kind.replace('_',' ').title()} | camera={self.camera} | {d['label']} ID={d['id']}"
        print("[EVENT]",msg); self.alerter.send(msg,path)
    def process(self,frame):
        detections=self.detector.track(frame); vis=frame.copy(); h,w=vis.shape[:2]
        if self.zone:
            poly=denormalize_polygon(self.cfg["zone"]["polygon"],w,h)
            cv2.polylines(vis,[np.array(poly)],True,(0,255,255),2)
            for kind,d in self.zone.update(detections):
                if kind=="enter": self._record(frame,"zone_intrusion",d)
        if self.rail:
            for kind,d in self.rail.update(detections): self._record(frame,kind,d)
        if self.fall:
            for kind,d in self.fall.update(detections): self._record(frame,kind,d)
        if self.fire_detector:
            fire_detections=self.fire_detector.track(frame)
            allowed={str(x).lower() for x in self.fire_cfg.get("classes",["fire","smoke"])}
            for d in fire_detections:
                if d["label"].lower() in allowed:
                    self._record(frame,"fire_smoke",d)
                    x1,y1,x2,y2=d["box"]
                    cv2.rectangle(vis,(x1,y1),(x2,y2),(0,0,255),3)
                    cv2.putText(vis,"FIRE/SMOKE",(x1,max(20,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,255),2)
        for d in detections:
            x1,y1,x2,y2=d["box"]; cv2.rectangle(vis,(x1,y1),(x2,y2),(255,80,0),2)
            cv2.putText(vis,f'{d["label"]} #{d["id"]} {d["confidence"]:.2f}',(x1,max(20,y1-7)),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),2)
        return vis
