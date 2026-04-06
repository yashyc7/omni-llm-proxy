from pydantic import BaseModel
from dataclasses import dataclass

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    provider: str

@dataclass(frozen=True)
class ProviderConfig:
    url: str
    input_selector: str
    submit_selector: str
    response_selector: str
    done_selector: str
    system_prompt: str
