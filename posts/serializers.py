from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Category, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'user', 'profile_picture','bio','created_at'
        ]
        
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    category = CategorySerializer(many=True, read_only= True)
    class Meta:
        model = Post
        fields = ['id','title', 'body', 'created_at', 'status',
                   'updated_at', 'author', 'category', 'thumbnail'
                  ]
        
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'created_at']
        read_only_fields = ["post"]

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(write_only= True)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only= True)