from django.db import models
from django.utils import timezone


class Task(models.Model):
    class CompletedStatus(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        COMPLETED = 2, 'Completed'

    title = models.CharField(max_length=100)
    completed = models.IntegerField(choices=CompletedStatus.choices, default=CompletedStatus.NOT_STARTED)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=['deleted_at'])
            return None
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])