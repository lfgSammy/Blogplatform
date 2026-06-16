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
    
    def validate_name(self, value):
        value = value.strip().title()

        if len(value)> 5:
            raise serializers.ValidationError(
                'A post cannot have more than 5 tags'
            )

        if Tag.objects.filter(name__iexact = value).exists():
            raise serializers.ValidationError(
                f'Tag{value} already exist'
            )
        return value

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
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    thumbnail_url = serializers.SerializerMethodField()

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'status', 'thumbnail',
                  'thumbnail_url', 'author', 'category', 'category_name',
                  'tags', 'tag_names', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at', 'thumbnail_url']
    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        tag_names = validated_data.pop('tag_names', [])

        # get or create category
        if category_name:
            category, created = Category.objects.get_or_create(
                name__iexact=category_name,
                defaults={
                    'name': category_name,
                    'created_by': self.context['request'].user
                }
            )
            validated_data['category'] = category

        # create the post
        post = super().create(validated_data)

        # get or create tags and add to post
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name__iexact=tag_name,
                defaults={'name': tag_name}
            )
            post.tags.add(tag)

        return post

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category_name', None)
        tag_names = validated_data.pop('tag_names', None)

        # update category
        if category_name:
            category, created = Category.objects.get_or_create(
                name__iexact=category_name,
                defaults={
                    'name': category_name,
                    'created_by': self.context['request'].user
                }
            )
            validated_data['category'] = category

        # update post
        post = super().update(instance, validated_data)

        # update tags if provided
        if tag_names is not None:
            post.tags.clear()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name__iexact=tag_name,
                    defaults={'name': tag_name}
                )
                post.tags.add(tag)

        return post

        
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