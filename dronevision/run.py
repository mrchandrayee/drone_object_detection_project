import argparse,cv2
from pathlib import Path
from .config import load_config
from .pipeline import DroneVisionPipeline
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/default.yaml")
    args=ap.parse_args(); cfg=load_config(args.config)
    source=int(args.source) if args.source.isdigit() else args.source
    cap=cv2.VideoCapture(source)
    if not cap.isOpened(): raise SystemExit(f"Cannot open source: {args.source}")
    ok,frame=cap.read()
    if not ok: raise SystemExit("No frames received")
    h,w=frame.shape[:2]; pipe=DroneVisionPipeline(cfg,(w,h)); fps=cap.get(cv2.CAP_PROP_FPS) or 25
    out=None
    if cfg.get("video",{}).get("save",True):
        folder=Path(cfg.get("output","runs")); folder.mkdir(parents=True,exist_ok=True)
        out=cv2.VideoWriter(str(folder/"annotated.mp4"),cv2.VideoWriter_fourcc(*"mp4v"),fps,(w,h))
    try:
        while ok:
            vis=pipe.process(frame)
            if out: out.write(vis)
            if cfg.get("video",{}).get("display",True):
                cv2.imshow("Drone Object Detection",vis)
                if cv2.waitKey(1)&0xFF==ord("q"): break
            ok,frame=cap.read()
    finally:
        cap.release()
        if out: out.release()
        cv2.destroyAllWindows()
if __name__=="__main__": main()
