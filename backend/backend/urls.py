"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.Home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import TemplateView
from trace_app.views import LabelingView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('get_trace_list', LabelingView.get_trace_list, name='get_trace_list'),
    path('get_topo_data', LabelingView.get_topo_data, name='get_topo_data'),
    path('get_gantt_data', LabelingView.get_gantt_data, name='get_gantt_data'),
    path('export_labels', LabelingView.export_labels, name='export_labels'),
    path('anomaly_period', LabelingView.anomaly_period, name='anomaly_period'),
    path('get_period', LabelingView.get_period, name='get_period'),
    path('get_fscore_and_services', LabelingView.get_fscore_and_services, name='get_fscore_and_services'),
    path('export_groundtruth', LabelingView.export_groundtruth, name='export_groundtruth'),
    
    re_path(r'^$', TemplateView.as_view(template_name='index.html'))
]
