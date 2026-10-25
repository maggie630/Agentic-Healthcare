from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class PatientSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str
    external_identifier: str
    first_name: str
    last_name: str
    birth_date: str | None = None
    administrative_gender: str | None = None

class RecordDraftInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str = Field(min_length=1, max_length=80)
    record_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    encounter_date: str | None = Field(default=None, max_length=40)
    confidence: float | None = Field(default=None, ge=0, le=1)
    provenance: str = Field(default="synthetic_demo", min_length=1, max_length=120)
    created_by: str = Field(min_length=1, max_length=120)

class PatientSearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=100000)
