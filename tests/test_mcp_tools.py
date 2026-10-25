import pytest

def test_server_exposes_expected_tool_functions():
    pytest.importorskip("mcp", reason="Install requirements.txt to test MCP registration")
    from patient_store import server
    assert callable(server.get_patient)
    assert callable(server.search_patients)
    assert callable(server.save_record_draft)
    assert callable(server.approve_record)
