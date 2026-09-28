from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from feed.models import Notification

from .models import Comment, Highlight, Post, Reel, ReelComment, ReelRepost, Song, Story


@login_required
def create_post(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')
        location = request.POST.get('location', '')
        music = request.FILES.get('music')
        music_title = request.POST.get('music_title', '').strip()
        song_id = request.POST.get('song_id', '').strip()
        if image:
            post = Post.objects.create(user=request.user, image=image, caption=caption, location=location)
            if song_id:
                try:
                    song = Song.objects.get(pk=int(song_id))
                    post.song = song
                    post.music_title = song.artist + ' — ' + song.title
                    song.plays += 1
                    song.save(update_fields=['plays'])
                    post.save()
                except (Song.DoesNotExist, ValueError):
                    pass
            elif music:
                post.music = music
                post.music_title = music_title or music.name.rsplit('.', 1)[0]
                post.save()
            return redirect('feed')
    return render(request, 'posts/create_post.html')


@login_required
def search_songs(request):
    q = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    qs = Song.objects.all()
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(title__icontains=q) | Q(artist__icontains=q))
    if genre:
        qs = qs.filter(genre=genre)
    songs = qs[:30]
    data = [{
        'id': s.pk,
        'title': s.title,
        'artist': s.artist,
        'audio': s.audio.url,
        'cover': s.cover.url if s.cover else '',
        'genre': s.genre,
        'plays': s.plays,
    } for s in songs]
    return JsonResponse({'songs': data, 'genres': [{'value': c[0], 'label': c[1]} for c in Song.GENRE_CHOICES]})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('user', 'user__profile', 'song').prefetch_related('likes', 'comments__user', 'saved_by'), pk=pk)
    return render(request, 'posts/post_detail.html', {'post': post})


@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                actor=request.user,
                notif_type='like',
                text=f'{request.user.username} liked your post.',
                link=f'/posts/{post.pk}/',
            )
    return JsonResponse({'liked': liked, 'likes_count': post.likes_count})


@login_required
@require_POST
def comment_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    text = request.POST.get('text', '').strip()
    if text:
        Comment.objects.create(post=post, user=request.user, text=text)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                actor=request.user,
                notif_type='comment',
                text=f'{request.user.username} commented on your post.',
                link=f'/posts/{post.pk}/',
            )
        return JsonResponse({'ok': True, 'username': request.user.username, 'text': text})
    return JsonResponse({'ok': False}, status=400)


# ── Post Options (Edit, Delete, Save) ──

@login_required
@require_POST
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)
    caption = request.POST.get('caption', '').strip()
    location = request.POST.get('location', '').strip()
    post.caption = caption
    post.location = location
    post.save()
    return JsonResponse({'ok': True, 'caption': caption, 'location': location})


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)
    post.delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def save_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.saved_by.all():
        post.saved_by.remove(request.user)
        saved = False
    else:
        post.saved_by.add(request.user)
        saved = True
    return JsonResponse({'ok': True, 'saved': saved})


# ── Stories ──

@login_required
@require_POST
def create_story(request):
    image = request.FILES.get('image')
    if image:
        Story.objects.create(user=request.user, image=image)
    return redirect('feed')


@login_required
def view_stories(request, username):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, username=username)
    cutoff = timezone.now() - timezone.timedelta(hours=24)
    stories = user.stories.filter(created_at__gte=cutoff)
    pic = user.profile.profile_pic.url if user.profile.profile_pic else ''
    data = [{
        'image': s.image.url,
        'time': s.created_at.strftime('%Hh ago') if (timezone.now() - s.created_at).seconds < 3600 * 12
                else s.created_at.strftime('%b %d'),
    } for s in stories]
    return JsonResponse({'username': user.username, 'pic': pic, 'stories': data})


# ── Highlights ──

@login_required
@require_POST
def create_highlight(request):
    title = request.POST.get('title', '').strip()
    if not title:
        return JsonResponse({'ok': False, 'error': 'Title required'}, status=400)
    highlight = Highlight.objects.create(user=request.user, title=title)
    if request.FILES.get('cover'):
        highlight.cover = request.FILES['cover']
        highlight.save()
    story_ids = request.POST.getlist('stories')
    if story_ids:
        stories = Story.objects.filter(pk__in=story_ids, user=request.user)
        highlight.stories.set(stories)
    return JsonResponse({
        'ok': True,
        'id': highlight.pk,
        'title': highlight.title,
        'cover': highlight.cover_url,
    })


@login_required
@require_POST
def edit_highlight(request, pk):
    highlight = get_object_or_404(Highlight, pk=pk)
    if highlight.user != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)
    title = request.POST.get('title', '').strip()
    if title:
        highlight.title = title
    if request.FILES.get('cover'):
        highlight.cover = request.FILES['cover']
    highlight.save()
    story_ids = request.POST.getlist('stories')
    if story_ids:
        stories = Story.objects.filter(pk__in=story_ids, user=request.user)
        highlight.stories.set(stories)
    return JsonResponse({
        'ok': True,
        'id': highlight.pk,
        'title': highlight.title,
        'cover': highlight.cover_url,
    })


@login_required
@require_POST
def delete_highlight(request, pk):
    highlight = get_object_or_404(Highlight, pk=pk)
    if highlight.user != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)
    highlight.delete()
    return JsonResponse({'ok': True})


@login_required
def highlight_stories(request, pk):
    highlight = get_object_or_404(Highlight.objects.select_related('user', 'user__profile'), pk=pk)
    stories = highlight.stories.all().order_by('created_at')
    pic = highlight.user.profile.profile_pic.url if highlight.user.profile.profile_pic else ''
    data = [{
        'image': s.image.url,
        'time': s.created_at.strftime('%b %d'),
    } for s in stories]
    return JsonResponse({
        'title': highlight.title,
        'username': highlight.user.username,
        'pic': pic,
        'stories': data,
    })


@login_required
def user_stories_list(request):
    stories = Story.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        'id': s.pk,
        'image': s.image.url,
        'time': s.created_at.strftime('%b %d, %Y'),
    } for s in stories]
    return JsonResponse({'stories': data})


# ── Reels ──

@login_required
def reels_view(request):
    reels = Reel.objects.all().select_related('user', 'user__profile').prefetch_related('likes', 'saved_by', 'comments')
    return render(request, 'posts/reels.html', {'reels': reels})


@login_required
def create_reel(request):
    if request.method == 'POST':
        video = request.FILES.get('video')
        caption = request.POST.get('caption', '')
        location = request.POST.get('location', '')
        if video:
            Reel.objects.create(user=request.user, video=video, caption=caption, location=location)
            return redirect('reels')
    return render(request, 'posts/create_reel.html')


@login_required
@require_POST
def like_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if request.user in reel.likes.all():
        reel.likes.remove(request.user)
        liked = False
    else:
        reel.likes.add(request.user)
        liked = True
        if reel.user != request.user:
            Notification.objects.create(
                recipient=reel.user,
                actor=request.user,
                notif_type='like',
                text=f'{request.user.username} liked your reel.',
                link='/reels/',
            )
    return JsonResponse({'liked': liked, 'likes_count': reel.likes_count})


@login_required
@require_POST
def delete_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if reel.user != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)
    reel.delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def comment_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    text = request.POST.get('text', '').strip()
    if text:
        ReelComment.objects.create(reel=reel, user=request.user, text=text)
        if reel.user != request.user:
            Notification.objects.create(
                recipient=reel.user,
                actor=request.user,
                notif_type='comment',
                text=f'{request.user.username} commented on your reel.',
                link='/reels/',
            )
        return JsonResponse({
            'ok': True,
            'username': request.user.username,
            'text': text,
            'pic': request.user.profile.profile_pic.url if request.user.profile.profile_pic else '',
        })
    return JsonResponse({'ok': False}, status=400)


@login_required
def reel_comments(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    comments = reel.comments.select_related('user', 'user__profile').all()
    data = [{
        'username': c.user.username,
        'text': c.text,
        'pic': c.user.profile.profile_pic.url if c.user.profile.profile_pic else '',
        'time': c.created_at.strftime('%b %d'),
    } for c in comments]
    return JsonResponse({'comments': data})


@login_required
@require_POST
def save_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if request.user in reel.saved_by.all():
        reel.saved_by.remove(request.user)
        saved = False
    else:
        reel.saved_by.add(request.user)
        saved = True
    return JsonResponse({'ok': True, 'saved': saved})


@login_required
@require_POST
def repost_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    repost, created = ReelRepost.objects.get_or_create(user=request.user, reel=reel)
    if not created:
        repost.delete()
        reposted = False
    else:
        reposted = True
        if reel.user != request.user:
            Notification.objects.create(
                recipient=reel.user,
                actor=request.user,
                notif_type='like',
                text=f'{request.user.username} reposted your reel.',
                link='/reels/',
            )
    return JsonResponse({'ok': True, 'reposted': reposted, 'count': reel.reposts.count()})
