from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_category_created_at'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE TABLE IF NOT EXISTS posts_tag (
                        id bigserial PRIMARY KEY,
                        name varchar(50) NOT NULL UNIQUE,
                        slug varchar(50) NOT NULL UNIQUE
                    );
                    CREATE TABLE IF NOT EXISTS posts_post_tags (
                        id bigserial PRIMARY KEY,
                        post_id bigint NOT NULL REFERENCES posts_post(id),
                        tag_id bigint NOT NULL REFERENCES posts_tag(id),
                        UNIQUE(post_id, tag_id)
                    );
                    """,
                    reverse_sql="""
                    DROP TABLE IF EXISTS posts_post_tags;
                    DROP TABLE IF EXISTS posts_tag;
                    """
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='Tag',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=50, unique=True)),
                        ('slug', models.SlugField(blank=True, unique=True)),
                    ],
                ),
                migrations.AddField(
                    model_name='post',
                    name='tags',
                    field=models.ManyToManyField(blank=True, related_name='posts', to='posts.tag'),
                ),
            ]
        ),
    ]