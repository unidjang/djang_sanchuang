from django.urls import path
from . import views

urlpatterns = [
    path('reg', views.reg),
    path('jwtlog', views.jwt_log),
    path('jwt_confirm', views.jwt_confirm),
    path('auth_info', views.auth_info),
    path('auth_update', views.auth_update),
]
