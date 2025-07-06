from django.urls import path
from . import views
app_name = 'dashboard'

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('save_class_location/', views.save_class_location, name='save_class_location'),
    path('delete_class/<pk>', views.delete_class, name='delete_class'),
    path('start_class/', views.start_class, name='start_class'),
    path('register_class/', views.register_class, name='register_class'),
    path('add_student/', views.add_student, name='add_student'),
    path('register_user/', views.register_user, name='register_user'),
]
