from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, Category, Tag

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

    def test_user_can_register(self):
        response = self.client.post(self.register_url, {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_cannot_register_with_weak_password(self):
        response = self.client.post(self.register_url, {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'weak'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_register_with_duplicate_username(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test2@test.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_register_with_duplicate_email(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.register_url, {
            'username': 'testuser2',
            'email': 'test@test.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_login(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_cannot_login_with_wrong_password(self):
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@1234'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # create two users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='Test@1234'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='Test@1234'
        )

        # create category
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            created_by=self.user1
        )

        # create tag
        self.tag = Tag.objects.create(
            name='Django',
            slug='django'
        )

        # create post for user1
        self.post = Post.objects.create(
            title='Test Post',
            body='This is a test post body that is long enough',
            status='published',
            author=self.user1,
            category=self.category
        )
        self.post.tags.add(self.tag)

        self.list_url = reverse('post-list')
        self.detail_url = reverse('post-detail', args=[self.post.id])

    # --- List Tests ---
    def test_anyone_can_get_posts(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_create_post(self):
        response = self.client.post(self.list_url, {
            'title': 'New Post',
            'body': 'Post body content here',
            'status': 'published'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_post(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {
            'title': 'New Post',
            'body': 'Post body content here that is long enough',
            'status': 'published',
            'category_name': 'Technology'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')

    def test_post_with_more_than_5_tags_fails(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {
            'title': 'New Post',
            'body': 'Post body content here',
            'status': 'published',
            'tag_names': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_duplicate_tags_fails(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {
            'title': 'New Post',
            'body': 'Post body content here',
            'status': 'published',
            'tag_names': ['Django', 'django']
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Detail Tests ---
    def test_anyone_can_get_single_post(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_author_can_update_own_post(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(self.detail_url, {
            'title': 'Updated Post',
            'body': 'Updated body content here that is long enough',
            'status': 'published'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Post')

    def test_non_author_cannot_update_post(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.detail_url, {
            'title': 'Hacked Post',
            'body': 'Hacked body',
            'status': 'published'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_post(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_non_author_cannot_delete_post(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    # --- Filter Tests ---
    def test_filter_posts_by_category(self):
        response = self.client.get(f'{self.list_url}?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_posts_by_tag(self):
        response = self.client.get(f'{self.list_url}?tag=django')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_posts(self):
        response = self.client.get(f'{self.list_url}?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CommentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='Test@1234'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='Test@1234'
        )

        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            status='published',
            author=self.user1
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Test comment'
        )

        self.list_url = reverse('comment-list', args=[self.post.id])
        self.detail_url = reverse('comment-detail', args=[self.post.id, self.comment.id])

    def test_anyone_can_read_comments(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_add_comment(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.list_url, {
            'content': 'Great post!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Great post!')

    def test_unauthenticated_user_cannot_comment(self):
        response = self.client.post(self.list_url, {
            'content': 'Great post!'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_delete_own_comment(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_non_author_cannot_delete_comment(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())


class LikeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='Test@1234'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='Test@1234'
        )

        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            status='published',
            author=self.user1
        )

        self.like_url = reverse('like', args=[self.post.id])

    def test_authenticated_user_can_like_post(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(
            user=self.user2, post=self.post).exists())

    def test_user_cannot_like_post_twice(self):
        self.client.force_authenticate(user=self.user2)
        self.client.post(self.like_url)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_unlike_post(self):
        Like.objects.create(user=self.user2, post=self.post)
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(
            user=self.user2, post=self.post).exists())

    def test_unauthenticated_user_cannot_like_post(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoryTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='Test@1234'
        )

        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            created_by=self.user1
        )

        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', args=['technology'])

    def test_anyone_can_get_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_create_category(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {
            'name': 'Lifestyle',
            'description': 'Posts about lifestyle'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_create_category(self):
        response = self.client.post(self.list_url, {
            'name': 'Lifestyle'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anyone_can_get_category_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category']['name'], 'Technology')

    def test_creator_can_delete_category(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(slug='technology').exists())