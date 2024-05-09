from django.db import models
from enum import Enum

class Span(models.Model):
    timestamp = models.CharField(max_length=100, default="")   
    cmdb_id = models.CharField(max_length=100, default="")
    span_id = models.CharField(max_length=100, default="")
    trace_id = models.CharField(max_length=100, default="")
    duration = models.IntegerField(default=0)
    type = models.CharField(max_length=100, default="")
    status_code = models.CharField(max_length=100, default="0")
    operation_name = models.CharField(max_length=200, default="")
    parent_span = models.CharField(max_length=100, default="")
    label = models.IntegerField(default=0)


class RCLLabel(models.Model):
    trace_id = models.CharField(max_length=100, default="")
    operation_name = models.CharField(max_length=200, default="")
    cmdb_id = models.CharField(max_length=100, default="")


class ProgressStatus(Enum):
    MODEL_TRAINING = 'Model training'
    COMPLETED = 'Completed'
    ANOMALY_LABELING = 'Anomaly labeling'
    ROOT_CAUSE_LABELING = 'Root Cause labeling'

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=200, default="")
    task_progress = models.CharField(max_length=100, default="25%")
    task_status = models.CharField(max_length=100, choices=[(status.value, status.name) for status in ProgressStatus], default=ProgressStatus.MODEL_TRAINING.value)
    task_time = models.DateTimeField(auto_now_add=True)
    learning_rate = models.FloatField(default=0.0001)
    batch_size = models.IntegerField(default=32)
    epoch = models.IntegerField(default=15)
    number_of_labels = models.IntegerField()


