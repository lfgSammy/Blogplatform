from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Comment, Like, Profile
from django.contrib.auth.models import User


# Signal 1 — auto create profile when user registers
@receiver(post_save, sender=User)
def create_user_profile(sender,instance,created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal 2 — send welcome email when user registers
@receiver(post_save, sender=User)
def send_welcome_email(sender,instance,created,**kwargs):
    if created:
        send_mail(
            subject='Welcome to Day2Day!',
            message=f'''
            Hi {instance.username},
            Welcome to Day2Day! Your account has been created successfully.

            You can now:
                - Write and publish blog posts
                - Comment and reply on other people's post
                - Like posts you enjoy

            Happy Blogging!!!

            Day2Day Team.
            ''',

            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list= [instance.email],
            fail_silently=True,
        )

# Signal 3 — notify post author when someone comments
@receiver(post_save, sender=Comment)
def notify_author_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        author = post.author
        commenter = instance.author

        # don't notify if author comments on their own post
        if author == commenter:
            return

        send_mail(
            subject=f'New comment on your post "{post.title}"',
            message=f'''
Hi {author.username},

{commenter.username} commented on your post "{post.title}":

"{instance.content}"

Visit your post to reply.

Blog Platform Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author.email],
            fail_silently=True,
        )

# Signal 4 — notify post author when someone likes their post
@receiver(post_save, sender=Like)
def notify_author_on_like(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        author = post.author
        liker = instance.user

        # don't notify if author likes their own post
        if author == liker:
            return

        send_mail(
            subject=f'Someone liked your post!',
            message=f'''
Hi {author.username},

{liker.username} liked your post "{post.title}".

Keep writing great content!

Blog Platform Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author.email],
            fail_silently=True,
        )
