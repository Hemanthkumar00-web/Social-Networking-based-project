import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from feed.models import Notification
from posts.models import Highlight, Post, Reel

from .models import Profile


@login_required
def profile_view(request, username):
    user = get_object_or_404(User.objects.select_related('profile'), username=username)
    posts = Post.objects.filter(user=user)
    reels = Reel.objects.filter(user=user)
    highlights = Highlight.objects.filter(user=user).prefetch_related('stories')
    is_following = request.user in user.profile.followers.all()
    follows_you = request.user.profile.followers.filter(pk=user.pk).exists() if user != request.user else False
    saved_posts = Post.objects.filter(saved_by=request.user) if user == request.user else []
    return render(request, 'profile_section/profile.html', {
        'profile_user': user,
        'posts': posts,
        'reels': reels,
        'highlights': highlights,
        'is_following': is_following,
        'follows_you': follows_you,
        'saved_posts': saved_posts,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip().lower()
        if new_username and new_username != request.user.username:
            if len(new_username) < 3:
                messages.error(request, 'Username must be at least 3 characters.')
                return render(request, 'profile_section/edit_profile.html')
            if not re.fullmatch(r'[a-z0-9._]+', new_username):
                messages.error(request, 'Username can only contain letters, numbers, periods and underscores.')
                return render(request, 'profile_section/edit_profile.html')
            if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
                messages.error(request, 'That username is already taken.')
                return render(request, 'profile_section/edit_profile.html')
            request.user.username = new_username
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        profile.bio = request.POST.get('bio', '')
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'profile_section/edit_profile.html')


@login_required
@require_POST
def follow_toggle(request, username):
    user = get_object_or_404(User.objects.select_related('profile'), username=username)
    if user == request.user:
        return JsonResponse({'ok': False, 'error': 'Cannot follow yourself'}, status=400)
    profile = user.profile
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        following = False
    else:
        profile.followers.add(request.user)
        following = True
        Notification.objects.create(
            recipient=user,
            actor=request.user,
            notif_type='follow',
            text=f'{request.user.username} started following you.',
            link=f'/profile/{request.user.username}/',
        )
    follows_you = request.user.profile.followers.filter(pk=user.pk).exists()
    return JsonResponse({
        'ok': True,
        'following': following,
        'followers_count': profile.followers_count,
        'follows_you': follows_you,
    })


@login_required
@require_POST
def remove_follower(request, username):
    user = get_object_or_404(User, username=username)
    request.user.profile.followers.remove(user)
    return JsonResponse({
        'ok': True,
        'followers_count': request.user.profile.followers_count,
    })


@login_required
def settings_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        section = request.POST.get('section', '')
        if section == 'privacy':
            profile.is_private = request.POST.get('is_private') == 'on'
            profile.save()
            messages.success(request, 'Privacy settings updated.')
        elif section == 'save_images':
            profile.save_original_posts = request.POST.get('save_original_posts') == 'on'
            profile.save()
            messages.success(request, 'Save images setting updated.')
        elif section == 'tags_mentions':
            profile.allow_tags = request.POST.get('allow_tags', 'everyone')
            profile.allow_mentions = request.POST.get('allow_mentions', 'everyone')
            profile.save()
            messages.success(request, 'Tags & mentions settings updated.')
        elif section == 'comments':
            profile.allow_comments = request.POST.get('allow_comments', 'everyone')
            profile.save()
            messages.success(request, 'Comment settings updated.')
        elif section == 'block_user':
            username_to_block = request.POST.get('username', '').strip()
            if username_to_block:
                user_to_block = User.objects.filter(username=username_to_block).first()
                if user_to_block and user_to_block != request.user:
                    profile.blocked_users.add(user_to_block)
                    messages.success(request, f'Blocked {username_to_block}.')
                else:
                    messages.error(request, 'User not found.')
        elif section == 'unblock_user':
            uid = request.POST.get('user_id')
            if uid:
                profile.blocked_users.remove(int(uid))
                messages.success(request, 'User unblocked.')
        elif section == 'close_friends_add':
            username_cf = request.POST.get('username', '').strip()
            if username_cf:
                user_cf = User.objects.filter(username=username_cf).first()
                if user_cf and user_cf != request.user:
                    profile.close_friends.add(user_cf)
                    messages.success(request, f'Added {username_cf} to close friends.')
                else:
                    messages.error(request, 'User not found.')
        elif section == 'close_friends_remove':
            uid = request.POST.get('user_id')
            if uid:
                profile.close_friends.remove(int(uid))
                messages.success(request, 'Removed from close friends.')
        elif section == 'story_settings':
            hide_ids = request.POST.getlist('hide_story_from')
            profile.hide_story_from.set(hide_ids)
            messages.success(request, 'Story settings updated.')
        return redirect('settings')

    blocked = profile.blocked_users.all().select_related('profile')
    close_friends = profile.close_friends.all().select_related('profile')
    liked_posts = Post.objects.filter(likes=request.user).select_related('user')[:50]
    return render(request, 'profile_section/settings.html', {
        'profile': profile,
        'blocked_users': blocked,
        'close_friends_list': close_friends,
        'liked_posts': liked_posts,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new1 = request.POST.get('new_password', '')
        new2 = request.POST.get('confirm_password', '')
        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif len(new1) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
        elif new1 != new2:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new1)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('settings')
    return render(request, 'profile_section/change_password.html')


@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.profile.followers.all().select_related('profile')
    return render(request, 'profile_section/user_list.html', {
        'profile_user': user,
        'users_list': followers,
        'title': 'Followers',
        'is_own': user == request.user,
    })


@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(profile__followers=user).select_related('profile')
    return render(request, 'profile_section/user_list.html', {
        'profile_user': user,
        'users_list': following,
        'title': 'Following',
        'is_own': user == request.user,
    })
