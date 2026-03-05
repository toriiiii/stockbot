from inventory.models import Item
from django.db import transaction

@transaction.atomic
def try_resolve_event(event):
    """
    If an ingestion event has all required data,
    create the Item and delete the event.
    """
    if not event.classification or event.weight_grams is None:
        return False

    Item.objects.create(
        user=event.user,
        name=event.classification,
        initial_grams=event.weight_grams,
        current_grams=event.weight_grams,
        expires_at=event.expires_at,
    )

    event.delete()
    return True
