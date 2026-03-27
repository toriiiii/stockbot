import os
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import DeviceToken
from inventory.models import Item
from inventory.notifications import send_push_notification

CRON_SECRET = os.environ.get('CRON_SECRET', '')


def _check_secret(request):
    """Returns True if the request carries the correct cron secret."""
    return CRON_SECRET and request.headers.get('X-Cron-Secret') == CRON_SECRET


@api_view(['POST'])
@permission_classes([AllowAny])
def cron_check_expiring_items(request):
    """
    Checks for items expiring in 3 days, 1 day, and today.
    Sends one batched push notification per user per tier.
    Notification flags on the Item model prevent duplicate alerts.

    POST /api/internal/check-expiring-items/
    Header: X-Cron-Secret: <your secret>
    """
    if not _check_secret(request):
        return Response({'error': 'Unauthorized'}, status=403)

    today = timezone.now().date()
    total_notified = 0

    tiers = [
        {
            'days': 7,
            'flag': 'notified_expiring_soon',
            'title': '🗓️ Expiring in 7 days',
            'urgency': 'Plan to use them soon',
        },
        {
            'days': 0,
            'flag': 'notified_expiry_day',
            'title': '🚨 Expiring today',
            'urgency': 'Use them now or throw them out',
        },
    ]

    for tier in tiers:
        target_date = today + timedelta(days=tier['days'])

        items = Item.objects.filter(
            expires_at=target_date,
            **{tier['flag']: False},
        ).select_related('user')

        if not items.exists():
            continue

        # Group by user — one notification per user per tier
        user_items = {}
        for item in items:
            user_items.setdefault(item.user_id, []).append(item)

        for user_id, user_item_list in user_items.items():
            tokens = list(
                DeviceToken.objects.filter(
                    user_id=user_id
                ).values_list('token', flat=True)
            )
            if not tokens:
                continue

            names = ', '.join(i.name for i in user_item_list)

            send_push_notification(
                tokens=tokens,
                title=tier['title'],
                body=f'{names} — {tier["urgency"]}',
                data={'type': 'expiry_alert'},
            )
            total_notified += 1

        # Mark as notified to prevent re-sending
        items.update(**{tier['flag']: True})

    return Response({'status': 'ok', 'notifications_sent': total_notified})


@api_view(['POST'])
@permission_classes([AllowAny])
def cron_remove_absent_items(request):
    """
    Deletes items that have been in 'removed' status for over 24 hours.
    If an item left the fridge and never came back, it's considered consumed.

    POST /api/internal/remove-absent-items/
    Header: X-Cron-Secret: <your secret>
    """
    if not _check_secret(request):
        return Response({'error': 'Unauthorized'}, status=403)

    cutoff = timezone.now() - timedelta(hours=24)

    # Items that left the fridge and haven't returned within 24 hours
    absent_items = Item.objects.filter(
        status='removed',
        last_removed_at__lt=cutoff,
    )

    count = absent_items.count()
    names = list(absent_items.values_list('name', flat=True))
    absent_items.delete()

    return Response({'status': 'ok', 'removed': count, 'items': names})