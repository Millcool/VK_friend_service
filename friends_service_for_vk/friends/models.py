from django.db import models
from django.conf import settings

class User(models.Model):
    username = models.CharField(max_length=255)

    def __str__(self):
        return (self.username)


class FriendRequest(models.Model):
    from_user = models.IntegerField(default=0)
    to_user = models.IntegerField(default=0)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')


class Friendship(models.Model):
    user_id = models.IntegerField(default=0)
    friend_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.friend_id}"