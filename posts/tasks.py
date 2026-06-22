from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email_task(username, email):
    send_mail(
        subject='Welcome to Day2Day!',
        message=f"""
Hi {username},

Welcome to Day2Day blog platform, Your account has been created successfully.

you can now:
- Write and publish blog posts
- Comment on other posts
- Like posts you enjoy

Happy Blogging

Day2Day Blog Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True
    )

@shared_task
def send_comment_notification_task(author_username,
                                   author_email,commenter_username,post_title,content):
    send_mail(
        subject=f"New comment on your post:{post_title}",
        message=f"""
Hi {author_username},
{commenter_username} commented on your post "{post_title}":
"{content}"

Visit your post to reply

Day2Day Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[author_email],
        fail_silently=True,
    )

@shared_task
def send_like_notification_task(author_username, author_email,
                                 liker_username, post_title):
    send_mail(
        subject='Someone liked your post!',
        message=f'''
Hi {author_username},

{liker_username} liked your post "{post_title}".

Keep writing great content!

Blog Platform Team
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[author_email],
        fail_silently=True,
    )