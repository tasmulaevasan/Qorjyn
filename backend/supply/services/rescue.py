from django.db import transaction

from supply.models import RescueTransfer
from supply.services.inventory import apply_delta

TERMINAL_STATUSES = ("completed", "declined")


@transaction.atomic
def accept(transfer):
    """Проводит товар между складами, а не только меняет статус.

    Повторный приём недопустим: товар переехал бы дважды, и склад
    разошёлся бы с картой — тот же дефект, что был у повторной
    доставки заказа. Отдающая и принимающая стороны определяются
    первой точкой каждого бизнеса: модель резерва оперирует
    бизнесами, а не точками.
    """
    # Строка берётся под блокировку до проверки статуса: без неё две
    # одновременные попытки обе прочли бы "proposed" и провели товар
    # дважды — блокировка в apply_delta держит позицию склада, а не
    # сам перевод.
    transfer = RescueTransfer.objects.select_for_update().get(pk=transfer.pk)
    if transfer.status in TERMINAL_STATUSES:
        return transfer

    donor_location = transfer.from_business.locations.first()
    receiver_location = transfer.to_business.locations.first()

    if donor_location and receiver_location:
        apply_delta(
            transfer.product_id, donor_location.id, -transfer.quantity,
            source="rescue", note=f"Передача в {transfer.to_business.name}",
        )
        apply_delta(
            transfer.product_id, receiver_location.id, transfer.quantity,
            source="rescue", note=f"Приём от {transfer.from_business.name}",
        )
        transfer.status = "completed"
    else:
        transfer.status = "accepted"

    transfer.save()
    return transfer


@transaction.atomic
def decline(transfer):
    """Тот же захват строки, что и в accept(): TOCTOU симметричен паре.

    Отказ не двигает товар, поэтому цена гонки ниже, чем в accept(), но
    оставленная без блокировки половина симметричной пары читается как
    сигнал, что блокировка не была нужна вовсе.
    """
    transfer = RescueTransfer.objects.select_for_update().get(pk=transfer.pk)
    if transfer.status in TERMINAL_STATUSES:
        return transfer
    transfer.status = "declined"
    transfer.save()
    return transfer
