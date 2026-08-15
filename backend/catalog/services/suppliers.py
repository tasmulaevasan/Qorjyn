from django.db import transaction

from catalog.models import Supplier


@transaction.atomic
def update_reliability(supplier, on_time, short):
    """Пересчёт рейтинга по факту завершённой поставки.

    Строка берётся под блокировку: две одновременные доставки одного
    поставщика иначе прочли бы одни и те же счётчики, и одна отметка
    потерялась бы. Транзакция объявлена здесь, а не оставлена
    вызывающему: блокировка вне транзакции на Postgres — ошибка, а не
    тихий no-op, как на SQLite. Внутри advance_status этот блок
    становится точкой сохранения и ничего не меняет.
    """
    supplier = Supplier.objects.select_for_update().get(pk=supplier.pk)
    supplier.total_orders += 1
    if on_time:
        supplier.on_time_deliveries += 1
    if short:
        supplier.short_deliveries += 1
    if supplier.total_orders:
        supplier.reliability_score = round(
            supplier.on_time_deliveries / supplier.total_orders * 100
        )
    supplier.save()
    return supplier
