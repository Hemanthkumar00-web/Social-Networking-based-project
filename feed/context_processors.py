from feed.models import Notification
from messasing.models import Message


def navbar_counts(request):
    if request.user.is_authenticated:
        return {
            'unread_notif_count': Notification.objects.filter(recipient=request.user, is_read=False).count(),
            'unread_message_count': Message.objects.filter(receiver=request.user, is_read=False).count(),
        }
    return {}
