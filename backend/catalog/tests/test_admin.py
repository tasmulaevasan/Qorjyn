import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client


@pytest.fixture
def admin_client(db):
    call_command("seed_demo")
    User.objects.create_superuser("admin", "admin@example.com", "adminpass")
    client = Client()
    client.login(username="admin", password="adminpass")
    return client


def test_registered_models_are_reachable(admin_client):
    for path in [
        "/admin/catalog/product/",
        "/admin/catalog/supplier/",
        "/admin/catalog/productcategory/",
        "/admin/catalog/tool/",
        "/admin/businesses/business/",
        "/admin/supply/inventoryitem/",
        "/admin/supply/order/",
        "/admin/supply/purchasewave/",
        "/admin/bot/messageevent/",
    ]:
        assert admin_client.get(path).status_code == 200, path


def test_analytics_page_reports_platform_usage(admin_client):
    response = admin_client.get("/admin/analytics/")

    assert response.status_code == 200
    assert response.context["active_businesses"] == 3
    assert response.context["top_categories"]
    assert "average_savings" in response.context


def test_seed_demo_keeps_the_superuser(admin_client):
    """POST /api/reset вызывает seed_demo.

    Если бы очистка шла через flush, после каждого сброса приходилось бы
    заново заводить суперпользователя — на демонстрации это потеря минут.
    """
    call_command("seed_demo")
    assert User.objects.filter(username="admin").exists()


def test_delivery_history_cannot_be_edited_in_the_admin(admin_client):
    """Три журнала объявлены неизменяемыми — проверяем третий.

    Первые два закрыты правами на самих моделях, а история доставки
    доступна только как вложенная форма внутри заказа, поэтому её
    защита живёт в другом месте и легко теряется.
    """
    from django.contrib import admin as django_admin
    from django.test import RequestFactory

    from supply.admin import DeliveryEventInline
    from supply.models import Order

    inline = DeliveryEventInline(Order, django_admin.site)
    request = RequestFactory().get("/admin/")

    assert inline.has_add_permission(request, None) is False
    assert inline.has_change_permission(request, None) is False
    assert inline.can_delete is False


def test_journals_cannot_be_deleted_in_the_admin(admin_client):
    from django.contrib import admin as django_admin
    from django.test import RequestFactory

    from bot.admin import MessageEventAdmin
    from bot.models import MessageEvent
    from supply.admin import InventoryEventAdmin
    from supply.models import InventoryEvent

    request = RequestFactory().get("/admin/")

    assert InventoryEventAdmin(
        InventoryEvent, django_admin.site
    ).has_delete_permission(request) is False
    assert MessageEventAdmin(
        MessageEvent, django_admin.site
    ).has_delete_permission(request) is False
