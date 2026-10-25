from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from .config import approval_token, mcp_host, mcp_port, database_path
from .database import initialize
from .services import PatientStoreService

initialize()
service = PatientStoreService(approver_token=approval_token())
mcp = FastMCP("patient_store", host=mcp_host(), port=mcp_port())

@mcp.tool()
def get_patient(identifier: str) -> dict:
    """Get a synthetic patient by internal ID or unique external identifier."""
    try:
        return service.get_patient(identifier)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@mcp.tool()
def search_patients(query: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    """Search synthetic patients by name or identifier with bounded pagination."""
    try:
        return service.search_patients(query=query, limit=limit, offset=offset)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@mcp.tool()
def save_record_draft(patient_id: str, record_type: str, title: str, content: str,
                      created_by: str, encounter_date: str | None = None,
                      confidence: float | None = None, provenance: str = "synthetic_demo") -> dict:
    """Save a new record as draft. This tool never approves records."""
    try:
        return service.save_record_draft(patient_id=patient_id, record_type=record_type, title=title,
            content=content, created_by=created_by, encounter_date=encounter_date,
            confidence=confidence, provenance=provenance)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@mcp.tool()
def approve_record(record_id: str, approver_id: str, approval_token: str) -> dict:
    """Approve a draft using the configured local demo token and approver ID.

    This token-based gate is for local demonstration only, not production authentication.
    """
    try:
        return service.approve_record(record_id, approver_id, approval_token)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

if __name__ == "__main__":
    # FastMCP uses Streamable HTTP for local MCP client connections.
    mcp.run(transport="streamable-http")
