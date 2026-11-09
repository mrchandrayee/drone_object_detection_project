from ultralytics import YOLO
class Detector:
    def __init__(self, model, confidence=.35, iou=.5, image_size=640, device="auto", classes=None):
        self.model=YOLO(model); self.confidence=confidence; self.iou=iou
        self.image_size=image_size; self.device=device; self.classes=classes
    def track(self, frame):
        kw=dict(source=frame,conf=self.confidence,iou=self.iou,imgsz=self.image_size,
                persist=True,verbose=False,tracker="bytetrack.yaml")
        if self.device!="auto": kw["device"]=self.device
        if self.classes is not None: kw["classes"]=self.classes
        result=self.model.track(**kw)[0]; names=result.names; out=[]
        if result.boxes is not None:
            for b in result.boxes:
                cid=int(b.cls[0]); tid=int(b.id[0]) if b.id is not None else -1
                out.append({"box":[int(v) for v in b.xyxy[0].tolist()],"id":tid,
                            "class_id":cid,"label":names.get(cid,str(cid)),"confidence":float(b.conf[0])})
        return out
