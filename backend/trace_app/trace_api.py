import sys
import pathlib
from trace_app.models import Span

trace_app_path = pathlib.Path(__file__).parent
sys.path.append(trace_app_path)


def get_span_list(trace_id):
    span_list = Span.objects.filter(trace_id=trace_id).values()
    print(list(span_list))
    return list(span_list)


def get_trace_list():
    trace_list = Span.objects.values('trace_id')
    return list(set(map(lambda x: x['trace_id'], trace_list)))
