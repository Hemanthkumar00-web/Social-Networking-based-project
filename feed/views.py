from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from posts.models import Post, Reel, Story
from profile_section.models import Profile

from .models import Notification


@login_required(login_url='login')
def feed(request):
    following_users = Profile.objects.filter(followers=request.user).values_list('user', flat=True)
    feed_users = list(following_users) + [request.user.id]
    posts = Post.objects.filter(user_id__in=feed_users).select_related('user', 'user__profile', 'song').prefetch_related('likes', 'comments', 'saved_by')

    cutoff = timezone.now() - timezone.timedelta(hours=24)
    stories_users = User.objects.filter(
        stories__created_at__gte=cutoff,
        id__in=feed_users,
    ).distinct().select_related('profile')
    my_stories = request.user.stories.filter(created_at__gte=cutoff)

    suggestions = User.objects.exclude(
        id__in=feed_users
    ).select_related('profile')[:5]

    return render(request, 'feed/home.html', {
        'posts': posts,
        'stories_users': stories_users,
        'my_stories': my_stories,
        'suggestions': suggestions,
    })


@login_required(login_url='login')
def search_view(request):
    return render(request, 'feed/search.html')


@login_required(login_url='login')
def search_api(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all')
    if len(q) < 1:
        return JsonResponse({'users': [], 'posts': [], 'reels': [], 'locations': []})

    data = {}

    if category in ('all', 'users'):
        users = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).select_related('profile')[:10]
        data['users'] = [{
            'username': u.username,
            'name': f'{u.first_name} {u.last_name}'.strip(),
            'pic': u.profile.profile_pic.url if u.profile.profile_pic else '',
        } for u in users]

    if category in ('all', 'posts'):
        posts = Post.objects.filter(
            Q(caption__icontains=q) | Q(location__icontains=q) | Q(user__username__icontains=q)
        ).select_related('user', 'user__profile')[:10]
        data['posts'] = [{
            'id': p.pk,
            'username': p.user.username,
            'caption': p.caption[:100],
            'location': p.location,
            'image': p.image.url,
            'likes': p.likes_count,
            'pic': p.user.profile.profile_pic.url if p.user.profile.profile_pic else '',
        } for p in posts]

    if category in ('all', 'reels'):
        reels = Reel.objects.filter(
            Q(caption__icontains=q) | Q(location__icontains=q) | Q(user__username__icontains=q)
        ).select_related('user', 'user__profile')[:10]
        data['reels'] = [{
            'id': r.pk,
            'username': r.user.username,
            'caption': r.caption[:100],
            'location': r.location,
            'likes': r.likes_count,
            'pic': r.user.profile.profile_pic.url if r.user.profile.profile_pic else '',
        } for r in reels]

    if category in ('all', 'locations'):
        post_locations = Post.objects.filter(
            location__icontains=q
        ).exclude(location='').values_list('location', flat=True).distinct()[:10]
        reel_locations = Reel.objects.filter(
            location__icontains=q
        ).exclude(location='').values_list('location', flat=True).distinct()[:10]
        all_locations = list(set(list(post_locations) + list(reel_locations)))[:10]
        location_results = []
        for loc in all_locations:
            post_count = Post.objects.filter(location__iexact=loc).count()
            reel_count = Reel.objects.filter(location__iexact=loc).count()
            location_results.append({
                'name': loc,
                'post_count': post_count,
                'reel_count': reel_count,
                'total': post_count + reel_count,
            })
        location_results.sort(key=lambda x: x['total'], reverse=True)
        data['locations'] = location_results

    return JsonResponse(data)


@login_required(login_url='login')
def location_view(request, location_name):
    posts = Post.objects.filter(location__iexact=location_name).select_related('user', 'user__profile')
    reels = Reel.objects.filter(location__iexact=location_name).select_related('user', 'user__profile')
    return render(request, 'feed/location.html', {
        'location_name': location_name,
        'posts': posts,
        'reels': reels,
    })


@login_required(login_url='login')
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('actor', 'actor__profile')[:50]
    return render(request, 'feed/notifications.html', {'notifs': notifs})


@login_required(login_url='login')
def notifications_api(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('actor', 'actor__profile')[:20]
    data = []
    for n in notifs:
        pic = n.actor.profile.profile_pic.url if n.actor.profile.profile_pic else ''
        data.append({
            'actor': n.actor.username,
            'pic': pic,
            'text': n.text,
            'time': n.created_at.strftime('%b %d'),
            'is_read': n.is_read,
            'link': n.link,
        })
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'notifications': data})


@login_required(login_url='login')
def mark_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})
