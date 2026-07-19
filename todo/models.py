from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    class CompletedStatus(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        COMPLETED = 2, 'Completed'

    title = models.CharField(max_length=100)
    completed = models.IntegerField(choices=CompletedStatus.choices, default=CompletedStatus.NOT_STARTED)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def __str__(self):
        return self.title