from django.urls import path
from . import views

urlpatterns = [
    path('add', views.add_note),
    path('list', views.list_view),
    path('update/<int:note_id>', views.update_note),
]
