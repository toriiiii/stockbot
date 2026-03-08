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
    
    best_match = match_item(event, candidates)
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
    
    best_match = match_item(event, candidates)
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
def match_item(event, candidates):
    best_match = None
    best_diff = None

    for candidate in candidates:
        diff = abs(candidate.current_grams - abs(event.weight_grams))
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_match = candidate

    return best_match