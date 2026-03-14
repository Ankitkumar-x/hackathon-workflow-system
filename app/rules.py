# python-engine/app/rules.py
from json_logic import jsonLogic
import copy

def evaluate_rules(rules, payload):
    """
    rules: list of dicts {id, condition, action}
    payload: dict
    returns: action (dict), traces (list)
    """
    context = {"payload": payload}
    traces = []

    for rule in rules:
        cond = rule.get("condition", {})
        try:
            result = bool(jsonLogic(cond, context))
        except Exception as e:
            result = False

        # record trace with input snippet
        traces.append({
            "rule_id": rule.get("id"),
            "condition": cond,
            "evaluated_to": result,
            "inputs": {k: payload.get(k) for k in (rule.get("audit_fields") or [])}
        })

        if result:
            # apply optional effects (we keep it simple - action returned)
            return rule.get("action", {"type": "manual_review"}), traces

    # default when no rule matched
    traces.append({
        "rule_id": None,
        "condition": "no_match",
        "evaluated_to": False,
        "inputs": {}
    })
    return {"type": "manual_review", "reason": "no_rule_matched"}, traces