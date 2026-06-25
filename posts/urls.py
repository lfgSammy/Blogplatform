from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name= 'post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name = 'post-detail'),
    path('posts/<int:pk>/comments/', views.CommentListView.as_view(), name='comment-list'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/', views.CommentDetailView.as_view()),
    path('posts/<int:pk>/like/', views.LikeView.as_view(), name = 'like'),
    path('auth/register/', views.RegisterView.as_view(), name= 'register'),
    path('auth/login/', views.LoginView.as_view(), name= 'login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('categories/', views.CategoryListView.as_view(), name='categories-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('tags/', views.TagListView.as_view(), name='tag'),
]