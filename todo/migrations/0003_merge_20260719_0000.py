from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_alter_task_completed'),
        ('todo', '0002_category_tag_task_category_task_tags'),
    ]

    operations = []
