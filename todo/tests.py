from django.test import TestCase,Client
from django.utils import timezone
from datetime import datetime
from todo.models import Task, Category, Tag
# Create your tests here.
class SampleTestCase(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 2, 3)

class TaskModelTestCase(TestCase):
    def test_create_task(self):
        due =timezone.make_aware(timezone.datetime(2024, 6, 30, 23, 59, 59))
        task = Task.objects.create(title='task1', due_at=due)
        task.save()

        task= Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertEqual(task.completed, Task.CompletedStatus.NOT_STARTED)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task=Task(title='task2')
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertEqual(task.completed, Task.CompletedStatus.NOT_STARTED)
        self.assertIsNone(task.due_at,None)
    
    def test_is_overdue_future(self):
        due=timezone.make_aware(timezone.datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(timezone.datetime(2024, 6,30, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()
        
        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due=timezone.make_aware(timezone.datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(timezone.datetime(2024, 7,1, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()
        
        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.make_aware(timezone.datetime(2024, 7,1, 0, 0, 0))
        task = Task(title='task1', due_at=None)
        task.save()
        
        self.assertFalse(task.is_overdue(current)) 
    
class TaskTagCategoryTestCase(TestCase):
    def test_create_task_with_category_and_tags(self):
        category = Category.objects.create(name='Work')
        tag1 = Tag.objects.create(name='study')
        tag2 = Tag.objects.create(name='urgent')

        task = Task.objects.create(title='task with category', category=category)
        task.tags.add(tag1, tag2)

        task.refresh_from_db()
        self.assertEqual(task.category, category)
        self.assertEqual(set(task.tags.values_list('name', flat=True)), {'study', 'urgent'})

    def test_index_post_with_category_and_tags(self):
        client = Client()
        response = client.post('/', {
            'title': 'Tagged Task',
            'due_at': '2024-06-30 23:59:59',
            'category': 'Work',
            'tags': 'study, urgent',
        })

        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(title='Tagged Task')
        self.assertEqual(task.category.name, 'Work')
        self.assertEqual(set(task.tags.values_list('name', flat=True)), {'study', 'urgent'})

class TaskViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)
    
    def test_index_post(self):
        client = Client()
        data = {'title':'Test Task', 'due_at':'2024-06-30 23:59:59'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)

    def test_index_get_order_post(self):
        task1 = Task(title='task1',due_at=timezone.make_aware(datetime(2024, 7,1 )))
        task1.save()
        task2 = Task(title='task2',due_at=timezone.make_aware(datetime(2024, 8,1 )))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title='task1',due_at=timezone.make_aware(datetime(2024, 7,1 )))
        task1.save()
        task2 = Task(title='task2',due_at=timezone.make_aware(datetime(2024, 8,1 )))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)
    
    def test_detail_get_success (self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime (2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)
        self.assertContains(response, 'Start')

    def test_detail_get_in_progress_shows_complete_button(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=Task.CompletedStatus.IN_PROGRESS,
        )
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete')
        self.assertNotContains(response, 'Start')

    def test_detail_get_completed_shows_no_advance_button(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=Task.CompletedStatus.COMPLETED,
        )
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Start')
        self.assertNotContains(response, '/advance/')
        self.assertNotContains(response, 'button type="submit"')
    
    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')
        self.assertEqual(response.status_code, 404)

    def test_update_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/edit/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        data = {
            'title': 'updated task',
            'due_at': '2024-08-01 23:59:59',
            'completed': str(Task.CompletedStatus.IN_PROGRESS),
        }
        response = client.post('/{}/edit/'.format(task.pk), data)

        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/{}/'.format(task.pk))
        self.assertEqual(task.title, 'updated task')
        self.assertEqual(task.due_at, timezone.make_aware(datetime(2024, 8, 1, 23, 59, 59)))
        self.assertEqual(task.completed, Task.CompletedStatus.IN_PROGRESS)

    def test_update_get_has_status_options(self):
        task = Task.objects.create(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        client = Client()
        response = client.get('/{}/edit/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not Started')
        self.assertContains(response, 'In Progress')
        self.assertContains(response, 'Completed')

    def test_delete_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/delete/'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_get_fail(self):
        client = Client()
        response = client.get('/1/delete/')

        self.assertEqual(response.status_code, 404)

    def test_close_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/close'.format(task.pk))

        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(task.completed, Task.CompletedStatus.COMPLETED)

    def test_close_get_fail(self):
        client = Client()
        response = client.get('/1/close')

        self.assertEqual(response.status_code, 404)

    def test_advance_status_from_not_started(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=Task.CompletedStatus.NOT_STARTED,
        )
        client = Client()
        response = client.post('/{}/advance/'.format(task.pk))

        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/{}/'.format(task.pk))
        self.assertEqual(task.completed, Task.CompletedStatus.IN_PROGRESS)

    def test_advance_status_from_in_progress(self):
        task = Task.objects.create(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=Task.CompletedStatus.IN_PROGRESS,
        )
        client = Client()
        response = client.post('/{}/advance/'.format(task.pk))

        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/{}/'.format(task.pk))
        self.assertEqual(task.completed, Task.CompletedStatus.COMPLETED)
