from django import views
from django.urls import path
from users import views


urlpatterns = [    
    path('create/', views.CreateUserAPIView.as_view(), name='create-user'),
    path('update/<int:pk>/', views.UpdateUserAPIView.as_view(), name='update-user'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
