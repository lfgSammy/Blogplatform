from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_category_created_at'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # don't touch the database
            state_operations=[
                migrations.CreateModel(
                    name='Tag',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=50, unique=True)),
                        ('slug', models.SlugField(blank=True, unique=True)),
                    ],
                ),
            ]
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # don't touch the database
            state_operations=[
                migrations.AddField(
                    model_name='post',
                    name='tags',
                    field=models.ManyToManyField(blank=True, related_name='posts', to='posts.tag'),
                ),
            ]
        ),
    ]