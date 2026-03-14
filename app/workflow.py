import json
from json_logic import jsonLogic
from .config_loader import load_config
from .db import SessionLocal
from .models import Request


def process_request(request_id: str):

    db = SessionLocal()

    req = db.query(Request).filter(Request.id == request_id).first()

    if not req:
        return

    config = load_config()

    workflow_name = req.workflow
    payload = req.payload

    workflow = config.get(workflow_name)

    if not workflow:
        req.status = "error"
        db.commit()
        return

    rules = workflow.get("rules", [])
    default_action = workflow.get("default_action", {}).get("type", "manual_review")

    decision = None

    for rule in rules:
        condition = rule.get("condition")

        if jsonLogic(condition, {"payload": payload}):
            decision = rule["action"]["type"]
            break

    if not decision:
        decision = default_action

    req.status = decision
    db.commit()

    db.close()