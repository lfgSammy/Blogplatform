from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Tag

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    tags = TagSerializer(many=True, read_only= True)
    class Meta:
        model = Post
        fields = ['id','title', 'body', 'created_at', 'status', 'updated_at', 'author', 'tags']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']
        read_only_fields = ["post"]

