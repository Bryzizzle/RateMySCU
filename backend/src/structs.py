from typing import Optional

from pydantic import BaseModel


class EvalRequest(BaseModel):
    id: Optional[str] = None
    classname: Optional[str] = None
    classcode: Optional[str] = None
    quarter: Optional[str] = None
    year: Optional[int] = None
    professor: Optional[str] = None
    overall: Optional[float] = None
    overallSearch: Optional[str] = None  # greaterThan, lessThan, equals