from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name= 'post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name = 'post-detail'),
    path('posts/<int:pk>/comments/', views.CommentListView.as_view()),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/', views.CommentDetailView.as_view()),
    path('posts/<int:pk>/like/', views.LikeView.as_view(), name = 'like'),
    path('auth/register/', views.RegisterView.as_view(), name= 'register'),
    path('auth/login/', views.LoginView.as_view(), name= 'login'),
]