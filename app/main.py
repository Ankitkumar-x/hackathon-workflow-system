# python-engine/app/main.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from .db import SessionLocal, init_db
from .models import RequestModel, IdempotencyKey, AuditLog
from sqlalchemy.exc import IntegrityError
import json
import uuid
app = FastAPI(title="Python Decision Engine")

class RequestInput(BaseModel):
    workflow: str
    payload: dict
    external_id: str | None = None

@app.on_event("startup")
def startup():
    init_db()

@app.post("/process", status_code=202)
def process(req: RequestInput, idempotency_key: str | None = Header(None)):
    db = SessionLocal()
    try:
        # 1) Idempotency by header if provided
        if idempotency_key:
            existing = db.query(IdempotencyKey).filter(IdempotencyKey.key == idempotency_key).first()
            if existing:
                # return stored snapshot if available
                return existing.response_snapshot or {"request_id": str(existing.request_id), "status": "exists"}

        # 2) External idempotency by workflow+external_id uniqueness also handled via DB constraint
        r = RequestModel(
            external_id=req.external_id,
            workflow=req.workflow,
            payload=req.payload,
            status="processing"
        )
        db.add(r)
        try:
            db.commit()
            db.refresh(r)
        except IntegrityError:
            # duplicate external_id for same workflow
            db.rollback()
            # find the existing request
            existing = db.query(RequestModel).filter(RequestModel.external_id == req.external_id, RequestModel.workflow == req.workflow).first()
            if existing:
                return {"request_id": str(existing.id), "status": existing.status}
            else:
                raise

        # save idempotency key mapping
        if idempotency_key:
            snapshot = {"request_id": str(r.id), "status": r.status}
            db.add(IdempotencyKey(key=idempotency_key, request_id=r.id, response_snapshot=snapshot))
            db.commit()

        # audit: created
        db.add(AuditLog(request_id=r.id, event_type="created", detail={"workflow": r.workflow}))
        db.commit()

        # enqueue background processing
        try:
            from .workflow import process_request
            process_request(str(r.id))
        except Exception as e:
            print("Workflow error:", e)

        return {"request_id": str(r.id), "status": r.status}
    finally:
        db.close()

@app.get("/requests/{request_id}")
def get_request(request_id: str):

    db = SessionLocal()

    try:
        request_uuid = uuid.UUID(request_id)

        req = db.query(RequestModel).filter(RequestModel.id == request_uuid).first()

        if req is None:
            return {"error": "Request not found"}

        return {
            "request_id": str(req.id),
            "workflow": req.workflow,
            "status": req.status,
            "payload": req.payload
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()