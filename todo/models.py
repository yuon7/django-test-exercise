from django.db import models
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, '高'),
        (PRIORITY_MEDIUM, '中'),
        (PRIORITY_LOW, '低'),
    ]

    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )

    def is_overdue(self,dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def priority_color(self):
        return {
            self.PRIORITY_HIGH: '#dc3545',
            self.PRIORITY_MEDIUM: '#ffc107',
            self.PRIORITY_LOW: '#28a745',
        }.get(self.priority, '#6c757d')