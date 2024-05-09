import request from '@/utils/request'


export function test (params) {
  return request({
    url: '/test',
    method: 'get',
    params
  })
}
export function get_trace_list (params) {
  return request({
    url: '/get_trace_list',
    method: 'get',
    params
  })
}
export function get_topo_data (params) {
  return request({
    url: '/get_topo_data',
    method: 'get',
    params
  })
}
export function get_gantt_data (params) {
  return request({
    url: '/get_gantt_data',
    method: 'get',
    params
  })
}
export function export_labels (params) {
  return request({
    url: '/export_labels',
    method: 'get',
    responseType: 'blob',
    params
  })
}
export function anomaly_period (params) {
  return request({
    url: '/anomaly_period',
    method: 'get',
    params
  })
}
export function get_period (params) {
  return request({
    url: '/get_period',
    method: 'get',
    params
  })
}
export function get_fscore_and_services (params) {
  return request({
    url: '/get_fscore_and_services',
    method: 'get',
    params
  })
}
export function export_groundtruth (params) {
  return request({
    url: '/export_groundtruth',
    method: 'get',
    responseType: 'blob',
    params
  })
}


