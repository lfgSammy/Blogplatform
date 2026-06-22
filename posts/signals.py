from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Comment, Like, Profile
from .tasks import (send_welcome_email_task,
                    send_comment_notification_task,
                    send_like_notification_task)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        # delay() sends the task to Celery instead of running it now
        send_welcome_email_task.delay(instance.username, instance.email)


@receiver(post_save, sender=Comment)
def notify_author_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        author = post.author
        commenter = instance.author
        if author == commenter:
            return
        send_comment_notification_task.delay(
            author.username,
            author.email,
            commenter.username,
            post.title,
            instance.content
        )


@receiver(post_save, sender=Like)
def notify_author_on_like(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        author = post.author
        liker = instance.user
        if author == liker:
            return
        send_like_notification_task.delay(
            author.username,
            author.email,
            liker.username,
            post.title
        )