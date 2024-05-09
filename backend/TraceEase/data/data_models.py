from dataclasses import dataclass
from datetime import datetime
from typing import *


@dataclass
class Span:
    
    trace_id: str
    span_id: str
    parent_span_id: str
    children_span_list: List['Span']
    
    start_time: datetime = None
    end_time: datetime = None
    duration: float = None

    service_name: str = None
    service_id: int = None

    operation_name: str = None
    operation_id: int = None
    
    status: str = None

    anomaly: int=0

    cmdb_id: str = None
    timestamp: int = 0

@dataclass
class Trace:

    trace_id: str
    root_span: Span
    span_count: int = 0
    anomaly: int = None


@dataclass
class CoverageTree:

    service_list: List[str]
    level_iteration: Tuple[str,...]

    def __hash__(self):
        return hash(self.level_iteration)
    
    def __eq__(self, obj):
        if obj is None:
            return False
        else:
            return self.level_iteration == obj.level_iteration