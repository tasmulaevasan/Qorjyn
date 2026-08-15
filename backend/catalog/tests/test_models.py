import pytest

from catalog.models import Product, ProductCategory, Supplier, SupplierPrice


@pytest.mark.django_db
def test_supplier_base_price_returns_dict_keyed_by_product_id():
    """Контракт фронтенда: supplier.basePrice[productId] -> цена.

    Цены хранятся отдельной моделью, чтобы их можно было редактировать
    в Django Admin, но наружу отдаются словарём.
    """
    dairy = ProductCategory.objects.create(code="dairy", name="Молочка", emoji="🥛")
    milk = Product.objects.create(
        id="prod-001", name="Молоко 3.2%", category=dairy, unit="л",
        min_stock=10, avg_daily_usage=6.5, shelf_life_days=5,
    )
    cream = Product.objects.create(
        id="prod-005", name="Сливки 10%", category=dairy, unit="л",
        min_stock=5, avg_daily_usage=2.0, shelf_life_days=7,
    )
    supplier = Supplier.objects.create(
        id="sup-001", name="Almaty Milk", phone="77071001010",
        min_order=5000, avg_delivery_hours=24, reliability_score=96,
        total_orders=48, on_time_deliveries=46, short_deliveries=1,
    )
    SupplierPrice.objects.create(supplier=supplier, product=milk, price=450)
    SupplierPrice.objects.create(supplier=supplier, product=cream, price=680)

    assert supplier.base_price == {"prod-001": 450, "prod-005": 680}
    assert sorted(supplier.product_ids) == ["prod-001", "prod-005"]
