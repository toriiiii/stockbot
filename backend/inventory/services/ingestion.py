from inventory.models import Item
from django.db import transaction
from django.utils import timezone

UNKNOWN_CLASS = "unknown"

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

    event.delete()
    return True

# ADD or RETURN item
def add_return_item(event):
    if event.classification == UNKNOWN_CLASS:
        create_new_item(event)
        return
    
    candidates = Item.objects.filter(
        user = event.user,
        classification = event.classification,
        status = "removed",
    )
    if not candidates.exists():
        create_new_item(event)
        return
    
    best_match = match_item(event, candidates, mode="return")
    mark_as_returned(event, best_match)
    return

# REMOVE item
def remove_item(event):
    if event.classification == UNKNOWN_CLASS:
        # TO DO: notify user
        return
    
    candidates = Item.objects.filter(
        user = event.user,
        classification = event.classification,
        status = "in_fridge",
    )
    if not candidates.exists():
        # TO DO: notify user
        return
    
    best_match = match_item(event, candidates, mode="remove")
    mark_as_removed(event, best_match)
    return

# Resolutions
def create_new_item(event):
    Item.objects.create(
        user=event.user,
        name=event.classification,
        initial_grams=event.weight_grams,
        current_grams=event.weight_grams,
        expires_at=event.expires_at,
    )
    return

def mark_as_removed(event, instance: Item):
    instance.status = "removed"
    instance.last_removed_at = timezone.now()
    instance.save()
    return

def mark_as_returned(event, instance: Item):
    instance.status = "in_fridge"
    instance.current_grams = event.weight_grams
    instance.save()

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