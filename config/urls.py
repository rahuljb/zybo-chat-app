from django.contrib import admin
from django.urls import path
from chat import views as chat_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', chat_views.register_view, name='register'),
    path('login/', chat_views.login_view, name='login'),
    path('logout/', chat_views.logout_view, name='logout'),

    path('chat/<int:user_id>/', chat_views.chat_view, name='chat'),
    path('', chat_views.user_list_view, name='user_list'),
]