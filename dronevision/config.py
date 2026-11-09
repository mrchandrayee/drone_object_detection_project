import yaml
def load_config(path):
    with open(path, encoding="utf-8") as f: cfg=yaml.safe_load(f) or {}
    cfg.setdefault("features", ["zone_intrusion"])
    cfg.setdefault("output", "runs")
    return cfg
