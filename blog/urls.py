from django.urls import path
from . import views

urlpatterns = [
    # 메인 페이지 (포스트 리스트)
    path('', views.PostList.as_view(), name='post_list'),
    
    # 포스트 디테일 페이지
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    
    # 카테고리 페이지
    path('category/<str:slug>/', views.category_page, name='category_page'),
    
    # 태그 페이지
    path('tag/<str:slug>/', views.tag_page, name='tag_page'),
]
