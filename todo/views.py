from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task, Category, Tag


def _parse_due_at(value):
    if not value:
        return None
    return make_aware(parse_datetime(value))


def _save_task(request, task=None):
    if task is None:
        task = Task()

    task.title = request.POST.get('title', '')
    task.due_at = _parse_due_at(request.POST.get('due_at'))

    category_name = request.POST.get('category', '').strip()
    if category_name:
        category, _ = Category.objects.get_or_create(name=category_name)
        task.category = category
    else:
        task.category = None

    task.save()

    task.tags.clear()
    for tag_name in [name.strip() for name in request.POST.get('tags', '').split(',') if name.strip()]:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        task.tags.add(tag)

    return task


# Create your views here.
def index(request):
    if request.method == 'POST':
        _save_task(request)

    tasks = Task.objects.select_related('category').prefetch_related('tags')

    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    context = {
        'tasks': tasks,
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    if request.method == 'POST':
        _save_task(request, task)
        return redirect('detail', task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task dose not exist')
    task.completed = True
    task.save()
    return redirect(index)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not exist')
    task.delete()
    return redirect(index)