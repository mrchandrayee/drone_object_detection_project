import sqlite3, time
from pathlib import Path
import cv2
class EventStore:
    def __init__(self, output):
        self.root=Path(output); self.root.mkdir(parents=True,exist_ok=True)
        self.images=self.root/"events"; self.images.mkdir(exist_ok=True); self.db=self.root/"events.db"
        with sqlite3.connect(self.db) as con:
            con.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,ts REAL,camera TEXT,kind TEXT,track_id INTEGER,label TEXT,snapshot TEXT)")
    def add(self, frame, camera, kind, track_id, label):
        ts=time.time(); path=self.images/f"{int(ts*1000)}_{kind}_{track_id}.jpg"
        cv2.imwrite(str(path),frame)
        with sqlite3.connect(self.db) as con:
            con.execute("INSERT INTO events(ts,camera,kind,track_id,label,snapshot) VALUES(?,?,?,?,?,?)",
                        (ts,camera,kind,track_id,label,str(path)))
        return path
