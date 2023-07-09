from django.db import models
from users.models import CustomUser
from django.utils import timezone

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_groups', blank=True, null=True)
    members = models.ManyToManyField(CustomUser, through='GroupMembership', related_name='groups',default=-1, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(Group, self).save(*args, **kwargs)
        return self

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(CustomUser, related_name='liked_messages', blank=True)

    def __str__(self):
        return f"Message by {self.sender.username} in {self.group.name}"
