import time
from collections import defaultdict
from .geometry import box_anchor, point_in_polygon
class ZoneMonitor:
    def __init__(self, polygon, anchor="bottom", grace_frames=2):
        self.polygon=polygon; self.anchor=anchor; self.grace=grace_frames
        self.inside=set(); self.misses=defaultdict(int)
    def update(self,detections):
        current=set(); events=[]
        for d in detections:
            tid=d["id"]
            if tid<0: continue
            if point_in_polygon(box_anchor(d["box"],self.anchor),self.polygon):
                current.add(tid); self.misses[tid]=0
                if tid not in self.inside: events.append(("enter",d))
            elif tid in self.inside:
                self.misses[tid]+=1
                if self.misses[tid]>self.grace: events.append(("leave",d))
        self.inside=(self.inside & current)|current
        for kind,d in events:
            if kind=="leave": self.inside.discard(d["id"])
        return events
class RailwayStallMonitor:
    def __init__(self,polygon,classes,stall_seconds=5,min_motion_px=2):
        self.polygon=polygon; self.classes=set(classes); self.delay=stall_seconds
        self.min_motion=min_motion_px; self.history={}; self.reported=set()
    def update(self,detections):
        now=time.time(); events=[]
        for d in detections:
            tid=d["id"]
            if tid<0 or d["label"].lower() not in self.classes: continue
            p=box_anchor(d["box"])
            if not point_in_polygon(p,self.polygon): continue
            old=self.history.get(tid)
            if old:
                moved=((p[0]-old[0][0])**2+(p[1]-old[0][1])**2)**.5
                if moved>=self.min_motion: self.history[tid]=(p,now); self.reported.discard(tid)
                elif now-old[1]>=self.delay and tid not in self.reported:
                    events.append(("railway_stall",d)); self.reported.add(tid)
            else: self.history[tid]=(p,now)
        return events
class FallHeuristic:
    # Bounding-box heuristic only; validate or replace with a trained pose classifier.
    def __init__(self,min_frames=5):
        self.counts=defaultdict(int); self.min_frames=min_frames; self.reported=set()
    def update(self,detections):
        events=[]
        for d in detections:
            tid=d["id"]
            if tid<0 or d["label"].lower()!="person": continue
            x1,y1,x2,y2=d["box"]; w=max(1,x2-x1); h=max(1,y2-y1)
            if w/h>1.15: self.counts[tid]+=1
            else: self.counts[tid]=0; self.reported.discard(tid)
            if self.counts[tid]>=self.min_frames and tid not in self.reported:
                events.append(("fall_detection",d)); self.reported.add(tid)
        return events
