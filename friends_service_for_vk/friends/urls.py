from django.urls import path

from . import views

app_name = 'friends'

urlpatterns = [

    path('', views.welcome_page, name='home'),
    path('users/register/', views.register_user, name='register_user'),
    path('users/log_in', views.log_in_user, name='log_in_user'),
    path('users/<int:user_id>/<int:friend_id>/remove_friend', views.remove_friend, name='delete_friend'),
    path('users/<int:user_id>/<int:friend_id>/friend_requests', views.user_page, name='friends_list_view'),
    path('users/<int:user_id>/<int:friend_id>/withdraw', views.withdraw, name='withdraw_request'),
    path('users/<int:user_id>/<int:friend_id>/<int:accepted>/add_friend', views.add_friend, name='add_friend'),
    path('users/<int:user_id>/friend_requests', views.friend_requests, name='friend_requests'),
    path('users/<int:user_id>/friend_list', views.friend_list, name='add_friend'),
    path('users/<int:user_id>/user_page', views.user_page, name='user_page'),

]
