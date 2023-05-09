from django.apps import AppConfig

# обращаемся сюда когда в settings.py находим 'friends'

class FriendsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'friends'
