from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max, Subquery, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from feed.models import Notification

from .models import Message


@login_required
def inbox(request):
    threads = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .values('sender', 'receiver')
        .annotate(last_msg=Max('created_at'))
        .order_by('-last_msg')
    )
    seen = set()
    thread_users = []
    for t in threads:
        other_id = t['receiver'] if t['sender'] == request.user.id else t['sender']
        if other_id not in seen:
            seen.add(other_id)
            thread_users.append(other_id)

    users = User.objects.filter(id__in=thread_users).select_related('profile')
    user_map = {u.id: u for u in users}
    ordered_users = [user_map[uid] for uid in thread_users if uid in user_map]

    unread_counts = {}
    for uid in thread_users:
        unread_counts[uid] = Message.objects.filter(sender_id=uid, receiver=request.user, is_read=False).count()

    last_messages = {}
    for uid in thread_users:
        msg = Message.objects.filter(
            Q(sender=request.user, receiver_id=uid) | Q(sender_id=uid, receiver=request.user)
        ).order_by('-created_at').first()
        if msg:
            last_messages[uid] = msg

    return render(request, 'messasing/inbox.html', {
        'thread_users': ordered_users,
        'unread_counts': unread_counts,
        'last_messages': last_messages,
    })


@login_required
def chat(request, username):
    other_user = get_object_or_404(User, username=username)
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related('sender').order_by('created_at')

    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    threads = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .values('sender', 'receiver')
        .annotate(last_msg=Max('created_at'))
        .order_by('-last_msg')
    )
    seen = set()
    thread_users_ids = []
    for t in threads:
        oid = t['receiver'] if t['sender'] == request.user.id else t['sender']
        if oid not in seen:
            seen.add(oid)
            thread_users_ids.append(oid)
    users = User.objects.filter(id__in=thread_users_ids).select_related('profile')
    user_map = {u.id: u for u in users}
    thread_users = [user_map[uid] for uid in thread_users_ids if uid in user_map]

    unread_counts = {}
    for uid in thread_users_ids:
        unread_counts[uid] = Message.objects.filter(sender_id=uid, receiver=request.user, is_read=False).count()

    return render(request, 'messasing/chat.html', {
        'other_user': other_user,
        'messages_list': messages_qs,
        'thread_users': thread_users,
        'unread_counts': unread_counts,
    })


@login_required
@require_POST
def send_message(request, username):
    other_user = get_object_or_404(User, username=username)
    body = request.POST.get('body', '').strip()
    if not body:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Empty message'}, status=400)
        return redirect('chat', username=username)
    msg = Message.objects.create(sender=request.user, receiver=other_user, body=body)
    Notification.objects.create(
        recipient=other_user,
        actor=request.user,
        notif_type='message',
        text=f'{request.user.username} sent you a message.',
        link=f'/messages/{request.user.username}/',
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'id': msg.pk,
            'body': msg.body,
            'created_at': msg.created_at.strftime('%H:%M'),
        })
    return redirect('chat', username=username)


@login_required
@require_POST
def unsend_message(request, pk):
    msg = get_object_or_404(Message, pk=pk, sender=request.user)
    msg.delete()
    return JsonResponse({'ok': True})


@login_required
def new_message(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        body = request.POST.get('body', '').strip()
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'messasing/new_message.html', {'error': 'User not found.'})
        if other_user == request.user:
            return render(request, 'messasing/new_message.html', {'error': 'You cannot message yourself.'})
        if body:
            Message.objects.create(sender=request.user, receiver=other_user, body=body)
            Notification.objects.create(
                recipient=other_user,
                actor=request.user,
                notif_type='message',
                text=f'{request.user.username} sent you a message.',
                link=f'/messages/{request.user.username}/',
            )
        return redirect('chat', username=username)
    return render(request, 'messasing/new_message.html')
