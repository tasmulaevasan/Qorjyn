from django.db import transaction

from supply.models import WaveParticipant


@transaction.atomic
def join(wave, business, quantity):
    participant, _ = WaveParticipant.objects.get_or_create(
        wave=wave, business=business, defaults={"quantity": quantity}
    )
    participant.quantity = quantity
    participant.confirmed = True
    participant.save()
    _refresh_status(wave)
    return wave


@transaction.atomic
def leave(wave, business):
    WaveParticipant.objects.filter(wave=wave, business=business).delete()
    _refresh_status(wave)
    return wave


def _refresh_status(wave):
    """Статус выводится из фактического набора участников.

    Волна может как достичь порога, так и опуститься обратно после выхода
    участника, поэтому переход считается в обе стороны.
    """
    if wave.status in ("ordered", "delivered", "cancelled"):
        return
    wave.status = "ready" if wave.total_quantity >= wave.target_quantity else "collecting"
    wave.save()
