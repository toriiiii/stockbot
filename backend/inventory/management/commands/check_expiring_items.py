from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from inventory.models import Item
from inventory.notifications import send_push_notification
from accounts.models import DeviceToken


class Command(BaseCommand):
    help = 'Send push notifications for items expiring at 7 days and today'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        # Three notification tiers
        # Each maps to a flag on the Item model to prevent duplicate alerts
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

            # Find items hitting this tier that haven't been notified yet
            items = Item.objects.filter(
                expires_at=target_date,
                **{tier['flag']: False},
            ).select_related('user')

            if not items.exists():
                self.stdout.write(f'No items expiring in {tier["days"]} day(s).')
                continue

            # Group by user so each user gets one notification per tier
            user_items = {}
            for item in items:
                user_items.setdefault(item.user_id, []).append(item)

            for user_id, user_item_list in user_items.items():
                # Get all push tokens for this user
                tokens = list(
                    DeviceToken.objects.filter(
                        user_id=user_id
                    ).values_list('token', flat=True)
                )

                if not tokens:
                    self.stdout.write(f'No device tokens for user {user_id}, skipping.')
                    continue

                # Combine all expiring item names into one notification
                names = ', '.join(i.name for i in user_item_list)

                send_push_notification(
                    tokens=tokens,
                    title=tier['title'],
                    body=f'{names} — {tier["urgency"]}',
                    data={'type': 'expiry_alert'},
                )

                self.stdout.write(
                    f'Notified user {user_id}: {names} ({tier["title"]})'
                )

            # Mark all items in this tier as notified to prevent re-sending
            items.update(**{tier['flag']: True})

        self.stdout.write(self.style.SUCCESS('Expiry check complete.'))