# Create your views here.
import os
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

import json
import pickle
from datetime import datetime
from TraceEase.utils import clean
import TraceEase.label 
import TraceEase.anomaly_period 
import TraceEase.spectrum 
import TraceEase.export_groundtruth 

data_file_path = "./TraceEase/data/data1/"
out_path = "./TraceEase/Output"


@csrf_exempt
@require_http_methods(['GET'])
class LabelingView(View):
    def get_trace_list(request):
        with open(os.path.join(out_path,"chosedid2trace.pkl"),'br') as f:
            chosedid2trace = pickle.load(f)
        res = []
        for trace_id,trace in chosedid2trace.items():
            res.append([trace_id,trace.root_span.operation_name])
        return JsonResponse(res, safe=False, status=200)
    def get_topo_data(request):
        with open(os.path.join(out_path,"chosedid2trace.pkl"),'br') as f:
            chosedid2trace = pickle.load(f)
        trace = chosedid2trace[request.GET.get('trace_id')]
        stack = [trace.root_span]
        nodes = []
        edges = []
        while len(stack)!=0:
            span = stack.pop()
            stack.extend(span.children_span_list)
            node_label = span.operation_name.split("/")[-1]
            if len(node_label)>12:
                node_label = node_label[:9]+"..."
            nodes.append({"id":span.span_id,"label":node_label,"shape": 'circle',"duration":span.duration,"status":200 if span.status=='0' else span.status,"service_name":span.cmdb_id,"strat_time":span.start_time.strftime('%Y-%m-%d %H:%M:%S'),"operation_name":span.operation_name.split("/")[-1],'color':'#cbdaf6'})
            for child in span.children_span_list:
                edges.append({"from":span.span_id,"to":child.span_id})
        return JsonResponse({"nodes":nodes,"edges":edges}, safe=False, status=200)
    def get_gantt_data(request):
        with open(os.path.join(out_path,"statistic","path2duration.json")) as f:
            path2duration = json.load(f)
        with open(os.path.join(out_path,"chosedid2trace.pkl"),'br') as f:
            chosedid2trace = pickle.load(f)
        trace = chosedid2trace[request.GET.get('trace_id')]
        max_duration = trace.root_span.duration
        min_duration = 0
        stack=[trace.root_span]
        id2span={}
        while len(stack)!=0:
            span = stack.pop()
            stack.extend(span.children_span_list)
            id2span[span.span_id] = span

        res = []

        def get_call_path(span,call_path_list):
            call_path_list.append(clean(f"{span.cmdb_id} {span.operation_name}".lower()))
            if span.parent_span_id in id2span:
                return get_call_path(id2span[span.parent_span_id],call_path_list)
            else:
                return call_path_list

        def backtracking(span):
            call_path_list = get_call_path(span,[])
            call_path_list.reverse()
            call_path = '#'.join(call_path_list)

            node = {}
            node["cmdb_id"]=span.cmdb_id
            node['id'] = span.span_id
            node['duration'] = span.duration
            node['length'] = (node['duration']-min_duration)/(max_duration-min_duration)
            node['operation_name'] = span.operation_name
            node['parentId']=span.parent_span_id
            node['startTime']=span.start_time.strftime('%Y-%m-%d %H:%M:%S')
            node['status_code']=span.status
            node['children'] = []
            node['call_path'] = path2duration[call_path]
            for child in span.children_span_list:
                node['children'].append(backtracking(child))
            return node
        res.append(backtracking(trace.root_span))
        return JsonResponse(res, safe=False, status=200)
    def export_labels(request):
        traceId2label = request.GET.get('params')
        traceId2label = json.loads(traceId2label)
        with open(os.path.join(out_path,"chosed_trace_id.json")) as f:
            chosed_trace_id = json.load(f)
        chosed_trace_labels = []
        for trace_id in chosed_trace_id:
            chosed_trace_labels.append(traceId2label[trace_id])
        with open(os.path.join(out_path,"chosed_trace_labels.json"),'w') as f:
            json.dump(chosed_trace_labels,f)
        TraceEase.label.main(out_path,data_file_path)
        response = HttpResponse(open(os.path.join(data_file_path,"labels.csv"), 'rb').read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="exported_trace_lables.csv"'
        return response
    def anomaly_period(request):
        TraceEase.anomaly_period.main(out_path,data_file_path)
        return JsonResponse("ok", safe=False, status=200)
    def get_period(request):
        with open(os.path.join(out_path,"anomaly_period.json")) as f:
            anomaly_period = json.load(f)
        timestamp2str = lambda x:datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
        res = []
        for start,end in anomaly_period:
            res.append([timestamp2str(start),timestamp2str(end)])
        return JsonResponse(res, safe=False, status=200)
    def get_fscore_and_services(request):
        index = int(request.GET.get('index'))
        with open(os.path.join(out_path,"anomaly_period.json")) as f:
            anomaly_period_list = json.load(f)
        nodes,edges = TraceEase.spectrum.main(anomaly_period_list[index],out_path,data_file_path)
        res={"nodes":nodes,"edges":edges}
        return JsonResponse(res, safe=False, status=200)
    def export_groundtruth(request):
        period2label = request.GET.get('params')
        period2label = json.loads(period2label)
        rcl_label = {"service":[],"failure_type":[]}
        for _,label in period2label.items():
            rcl_label['service'].append(label[0])
            rcl_label['failure_type'].append(label[1])
        with open(os.path.join(out_path,"rcl_label.json"),'w') as f:
            json.dump(rcl_label,f)
        TraceEase.export_groundtruth.main(out_path,data_file_path)

        response = HttpResponse(open(os.path.join(data_file_path,"groundtruth.json"), 'rb').read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="groundtruth.json"'
        return response
        
        
