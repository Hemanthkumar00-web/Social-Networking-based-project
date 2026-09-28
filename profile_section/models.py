from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='following_profiles', blank=True)
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    close_friends = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='close_friend_of', blank=True)
    blocked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='blocked_by', blank=True)
    save_original_posts = models.BooleanField(default=False)
    allow_tags = models.CharField(max_length=20, default='everyone', choices=[('everyone', 'Everyone'), ('following', 'People You Follow'), ('none', 'No One')])
    allow_mentions = models.CharField(max_length=20, default='everyone', choices=[('everyone', 'Everyone'), ('following', 'People You Follow'), ('none', 'No One')])
    allow_comments = models.CharField(max_length=20, default='everyone', choices=[('everyone', 'Everyone'), ('following', 'People You Follow')])
    hide_story_from = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='hidden_stories_from', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return Profile.objects.filter(followers=self.user).count()
