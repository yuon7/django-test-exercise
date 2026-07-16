from django.db import models
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    class CompletedStatus(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        COMPLETED = 2, 'Completed'

    title = models.CharField(max_length=100)
    completed = models.IntegerField(choices=CompletedStatus.choices, default=CompletedStatus.NOT_STARTED)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)

    def is_overdue(self,dt):
        if self.due_at is None:
            return False
        return self.due_at < dt