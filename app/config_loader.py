# python-engine/app/config_loader.py
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../configs/workflow.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)