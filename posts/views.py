from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        if not email or not username or not password:
            return Response({'error': "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': "Username already exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username= username,
            password= password,
            email= email
        )
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status= status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class PostListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request):
        posts = Post.objects.all()
        serializers = PostSerializer(posts, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        serializers = PostSerializer(data= request.data)
        if serializers.is_valid():
            serializers.save(author = request.user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return[IsAuthenticated()]
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None
        
    def get(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error': 'Post not found'}, status= status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    def put(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response({'error': 'You are not allowed to edit this post'}, status=status.HTTP_403_FORBIDDEN)
        serializer= PostSerializer(post, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'error':'Post not found'}, status= status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response({'error': 'You are not allowed to delete this post'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

class CommentListView(APIView):
     def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
     def get(self, request, pk):
         comments = Comment.objects.filter(post_id = pk)
         serializers = CommentSerializer(comments, many=True)
         return Response(serializers.data)
     def post(self, request, pk):
         serializers =CommentSerializer(data = request.data)
         if serializers.is_valid():
             serializers.save(author = request.user, post_id = pk)
             return Response(serializers.data, status= status.HTTP_201_CREATED)
         return Response(serializers.errors, status= status.HTTP_400_BAD_REQUEST)
     

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, comment_pk):
        try:
            return Comment.objects.get(pk= comment_pk)
        except Comment.DoesNotExist:
            return None
    def delete(self, request, post_pk, comment_pk):
        comment = self.get_object(comment_pk)
        if not comment:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        if comment.author != request.user:
            return Response({"error": "You are not allowed to delete this post"}, 
                            status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not Found"}, status=status.HTTP_404_NOT_FOUND)
        if Like.objects.filter(user= request.user, post= post).exists():
            return Response({"error": "You already liked this post"}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user= request.user, post=post)
        return Response({"Message": "Post Liked"}, status=status.HTTP_201_CREATED)
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        like = Like.objects.filter(user= request.user, post=post).first()
        if not like:
            return Response({'error': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({'message': 'Post unliked'}, status=status.HTTP_204_NO_CONTENT)