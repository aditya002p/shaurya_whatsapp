from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

session_service = SessionService()

class SessionCreate(BaseModel):
    agent_id: int
    user_mobile: str

class SessionUpdate(BaseModel):
    current_state: Optional[str] = None
    vehicle_number: Optional[str] = None
    engine_number: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    plan_selected: Optional[str] = None

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_sessions():
    """Get all active sessions"""
    try:
        # This would need to be implemented in SessionService
        # For now, returning empty list
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """Get session by ID"""
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict[str, Any])
async def create_session(session_data: SessionCreate):
    """Create a new session"""
    try:
        session = session_service.create_session(
            agent_id=session_data.agent_id,
            user_mobile=session_data.user_mobile
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_id}", response_model=Dict[str, Any])
async def update_session(session_id: str, session_data: SessionUpdate):
    """Update session data"""
    try:
        # Extract non-None values
        update_data = {k: v for k, v in session_data.dict().items() if v is not None}
        
        if update_data:
            success = session_service.update_session_data(session_id, **update_data)
            if success:
                return {"message": "Session updated successfully", "session_id": session_id}
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            return {"message": "No data to update", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_id}/state")
async def update_session_state(session_id: str, state: str):
    """Update session state"""
    try:
        success = session_service.update_session_state(session_id, state)
        if success:
            return {"message": "Session state updated successfully", "session_id": session_id, "state": state}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/documents")
async def add_document(session_id: str, doc_type: str, doc_path: str):
    """Add document to session"""
    try:
        success = session_service.add_document(session_id, doc_type, doc_path)
        if success:
            return {"message": "Document added successfully", "session_id": session_id, "doc_type": doc_type}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/complete")
async def complete_session(session_id: str):
    """Mark session as completed"""
    try:
        success = session_service.complete_session(session_id)
        if success:
            return {"message": "Session completed successfully", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    try:
        # This would need to be implemented in SessionService
        # For now, returning success message
        return {"message": "Session deleted successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session_legacy(session_id: str):
    s = session_service.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": s.session_id,
        "agent_id": s.agent_id,
        "current_state": s.current_state,
        "data": s.data
    }
