from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Category, Profile, Tag

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

class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count']
        read_only_fields = ['slug']


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 
                  'created_by', 'post_count', 'created_at']
        read_only_fields = ['slug', 'created_by', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    category = CategorySerializer(read_only= True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset= Category.objects.all(), source = 'category',
        write_only = True, required = False
    )
    tags = TagSerializer(many= True, read_only = True)
    class Meta:
        model = Post
        fields = ['id','title', 'body', 'created_at', 'category_id','status',
                   'updated_at', 'author', 'category', 'thumbnail', 'tags'
                  ]
        read_only_fields = ['author', 'created_at', 'updated_at']
        
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