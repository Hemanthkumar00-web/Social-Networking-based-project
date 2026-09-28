from django.conf import settings
from django.db import models


class Song(models.Model):
    GENRE_CHOICES = [
        ('pop', 'Pop'),
        ('hiphop', 'Hip Hop'),
        ('rnb', 'R&B'),
        ('rock', 'Rock'),
        ('electronic', 'Electronic'),
        ('indie', 'Indie'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('lofi', 'Lo-Fi'),
        ('bollywood', 'Bollywood'),
        ('latin', 'Latin'),
        ('kpop', 'K-Pop'),
        ('country', 'Country'),
        ('trending', 'Trending'),
    ]

    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    audio = models.FileField(upload_to='songs/')
    cover = models.ImageField(upload_to='song_covers/', blank=True, null=True)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default='pop')
    plays = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-plays', '-created_at']

    def __str__(self):
        return f'{self.artist} — {self.title}'


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField(max_length=2200, blank=True)
    location = models.CharField(max_length=255, blank=True)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    music = models.FileField(upload_to='post_music/', blank=True, null=True)
    music_title = models.CharField(max_length=255, blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.pk}'

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}...'


class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} story - {self.pk}'

    @property
    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds() > 86400


class Highlight(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='highlights')
    title = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='highlights/', blank=True)
    stories = models.ManyToManyField('Story', related_name='highlights', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.title}'

    @property
    def cover_url(self):
        if self.cover:
            return self.cover.url
        first = self.stories.first()
        if first:
            return first.image.url
        return ''


class Reel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reels')
    video = models.FileField(upload_to='reels/')
    caption = models.TextField(max_length=2200, blank=True)
    location = models.CharField(max_length=255, blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reels', blank=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_reels', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} reel - {self.pk}'

    @property
    def likes_count(self):
        return self.likes.count()


class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class ReelRepost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reel_reposts')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='reposts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'reel')
