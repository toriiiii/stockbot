from inventory.models import Item
from django.db import transaction
from django.utils import timezone
from inventory.notifications import send_push_notification
from accounts.models import DeviceToken

import logging

logger = logging.getLogger(__name__)

UNKNOWN_CLASS = "unknown"
TOLERANCE = 40
LOW_STOCK_THRESHOLD = 25 # percentage of initial weight

@transaction.atomic
def try_resolve_event(event):
    """
    If an ingestion event has all required data,
    determine whether the item is being ADDED, REMOVED, or RETURNED
    and update the database accordingly.
    """

    # Ingestion event does not have all required data
    if not event.classification or event.weight_grams is None:
        return False
    
    # Item is being ADDED or RETURNED
    if event.weight_grams > 0:
        add_return_item(event)
    else:
        remove_item(event)

    event.image = None # clear reference to preserve file
    event.save()
    event.delete()
    logger.info(f'Resolved sensor ingestion event — user={event.user} image_id={event.image_id}')
    return True

# ADD or RETURN item
def add_return_item(event):
    if event.classification == UNKNOWN_CLASS:
        create_new_item(event)
        return
    
    candidates = Item.objects.filter(
        user = event.user,
        name = event.classification,
        status = "removed",
    )
    if not candidates.exists():
        create_new_item(event)
        return
    
    best_match = match_item(event, candidates, mode="return")
    mark_as_returned(event, best_match)

    # send low stock notif if needed
    if (event.weight_grams / best_match.initial_weight) * 100 < LOW_STOCK_THRESHOLD:
        logger.info('Returned item is low stock')
        tokens = list(
            DeviceToken.objects.filter(user=best_match.user).values_list('token', flat=True)
        )
        send_push_notification(
            tokens=tokens,
            title='📦 Low stock alert',
            body=f'{best_match.name} is running low — only {event.weight_grams:.0f}g remaining.',
            data={
                'type': 'low_stock',
                'item_id': str(best_match.id),
            },
        )

    return

# REMOVE item
def remove_item(event):
    if event.classification == UNKNOWN_CLASS:
        logger.error(f'Unknown item has been removed')
        return
    
    candidates = Item.objects.filter(
        user = event.user,
        name = event.classification,
        status = "in_fridge",
    )
    if not candidates.exists():
        logger.error(f'Removed item does not exist')
        return
    
    best_match = match_item(event, candidates, mode="remove")
    mark_as_removed(event, best_match)
    return

# Resolutions
def create_new_item(event):
    item = Item(
        user=event.user,
        name=event.classification,
        initial_grams=event.weight_grams,
        current_grams=event.weight_grams,
        expires_at=event.expires_at,
    )
    item.image.name = event.image.name if event.image else None
    item.save()
    logger.info(f'Item has been created')
    return

def mark_as_removed(event, instance: Item):
    instance.status = "removed"
    instance.last_removed_at = timezone.now()
    instance.save()
    logger.info(f'Item has been removed')
    return

def mark_as_returned(event, instance: Item):
    instance.status = "in_fridge"
    instance.current_grams = event.weight_grams
    logger.info(f'Item has been returned')
    instance.save()
    return

# Matching algorithm
def match_item(event, candidates, mode):

    target_weight = abs(event.weight_grams)
    now = timezone.now()

    best_match = None
    best_score = None

    for candidate in candidates:

        weight_diff = abs(candidate.current_grams - target_weight)

        fifo_penalty = 0
        recency_penalty = 0

        if mode == "remove":
            if candidate.created_at:
                fifo_penalty = (now - candidate.created_at).total_seconds() * -0.0001

        if mode == "return":
            if candidate.last_removed_at:
                seconds_since_removed = (now - candidate.last_removed_at).total_seconds()
                recency_penalty = seconds_since_removed * 0.001

        score = weight_diff + fifo_penalty + recency_penalty

        if best_score is None or score < best_score:
            best_score = score
            best_match = candidate

    return best_match
