from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers as drf_serializers
from .models import Post, Comment, Like, Category, Tag
from .serializers import (PostSerializer, CommentSerializer, RegisterSerializer,
                          LoginSerializer, CategorySerializer, TagSerializer)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import re
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.pagination import CursorPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import PostFilter
from django.core.cache import cache
from .filters import PostFilter


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append('Password must at least be 8 characters')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least one number')
    return errors


class RegisterView(APIView):
    @extend_schema(request=RegisterSerializer, responses={201: None})
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        if not email or not username or not password:
            return Response({'error': 'All fields are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not validate_email(email):
            return Response({'error': 'Invalid email format'},
                            status=status.HTTP_400_BAD_REQUEST)
        password_errors = validate_password(password)
        if password_errors:
            return Response({'error': password_errors},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already existed'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            username=username, password=password, email=email)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    @extend_schema(request=LoginSerializer)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response({'error': 'Invalid Credentials'},
                        status=status.HTTP_401_UNAUTHORIZED)


class CategoryListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=CategorySerializer)
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @extend_schema(
            request=inline_serializer(
                name= 'CategoryCreate',
                fields= {
                    'name':drf_serializers.CharField(),
                    'description':drf_serializers.CharField(required=False),
                }
            ),
            responses=CategorySerializer
    )

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=CategorySerializer)
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},
                            status=status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(category=category, status='published')
        category_serializer = CategorySerializer(category)
        post_serializer = PostSerializer(posts, many=True)
        return Response({
            'category': category_serializer.data,
            'posts': post_serializer.data
        })

    @extend_schema(responses={204: None})
    def delete(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if category.created_by != request.user:
            return Response({'error': 'You cannot delete this category'},
                            status=status.HTTP_403_FORBIDDEN)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=TagSerializer)
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            name='TagCreate',
            fields={
                'name': drf_serializers.CharField(),
            }
        ),
        responses=TagSerializer
    )
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=PostSerializer)
    def get(self, request):

        cache_key = f"posts_list_{request.get.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        posts = Post.objects.select_related(
            'author',
            'author__profile',
            'category',
            'category__created_by'
        ).prefetch_related(
            'tags',
        ).filter(status='published')

        post_filter = PostFilter(request.GET, queryset=posts)
        posts = post_filter.qs

        ordering = request.query_params.get('ordering')
        if ordering in['created_at', '-created_at', 'title', '-title']:
            posts = posts.order_by(ordering)

            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)

        # filter by category slug
        category = request.query_params.get('category')
        if category:
            posts = posts.filter(category__slug=category)

        # filter by tag slug
        tag = request.query_params.get('tag')
        if tag:
            posts = posts.filter(tags__slug=tag)

        # search by title or body
        search = request.query_params.get('search')
        if search:
            posts = posts.filter(title__icontains=search)

        paginator = CursorPagination()
        paginator.page_size = 10
        paginator.ordering = '-created_at'
        paginated_posts = paginator.paginate_queryset(posts, request, view=self)

        if paginated_posts is not None:
            serializer = PostSerializer(paginated_posts, many= True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(request=PostSerializer)
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            cache.delete_pattern('posts_list_*')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        try:
            return Post.objects.select_related(
                'author',
                'author__profile',
                'category',
                'category__created_by'
            ).prefetch_related(
                'tags',
                'comments__author',
                'comments__author__profile',
            ).get(pk=pk)
        except Post.DoesNotExist:
            return None

    @extend_schema(responses=PostSerializer)
    def get(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error': 'Post not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @extend_schema(request=PostSerializer)
    def put(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error': 'Post not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response({'error': 'You are not allowed to edit this post'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern('posts_list_*')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error': 'Post not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response({'error': 'You are not allowed to delete this post'},
                            status=status.HTTP_403_FORBIDDEN)
        post.delete()
        cache.delete_pattern('posts_list_*')
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=CommentSerializer)
    def get(self, request, pk):
        comments = Comment.objects.filter(post_id=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(request=CommentSerializer)
    def post(self, request, pk):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_pk):
        try:
            return Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, post_pk, comment_pk):
        comment = self.get_object(comment_pk)
        if not comment:
            return Response({'error': 'Comment not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if comment.author != request.user:
            return Response({'error': 'You are not allowed to delete this comment'},
                            status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={201: None})
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({'error': 'You already liked this post'},
                            status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=request.user, post=post)
        return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'},
                            status=status.HTTP_404_NOT_FOUND)
        like = Like.objects.filter(user=request.user, post=post).first()
        if not like:
            return Response({'error': 'You have not liked this post'},
                            status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({'message': 'Post unliked'}, status=status.HTTP_204_NO_CONTENT)