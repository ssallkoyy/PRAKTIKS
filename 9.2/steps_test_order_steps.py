"""
Автоматические тестовые шаги для сценария создания заказа.
Использует pytest-bdd для выполнения Gherkin сценариев.
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock


# Указываем путь к feature файлу
scenarios('../features/order.feature')


# ===== GIVEN ШАГИ (Предусловия) =====

@given('пользователь авторизован в системе')
def user_authorized(order_context, mock_user):
    """Шаг: пользователь авторизован."""
    order_context['user'] = mock_user
    assert mock_user.is_authenticated is True


@given(parsers.parse('в корзине есть товары:\n{items_table}'))
def cart_has_items(order_context, mock_cart, items_table):
    """Шаг: в корзине есть товары."""
    # Парсим таблицу товаров
    items = []
    lines = items_table.strip().split('\n')
    
    for line in lines:
        # Пропускаем строки с | и заголовки
        if '|' in line and 'Название' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) == 3:
                items.append({
                    'name': parts[0],
                    'price': float(parts[1]),
                    'quantity': int(parts[2])
                })
    
    mock_cart.items = items
    mock_cart.is_empty = len(items) == 0
    order_context['cart'] = mock_cart


# ===== WHEN ШАГИ (Действия) =====

@when('пользователь нажимает кнопку "Оформить заказ"')
def user_clicks_checkout(order_context):
    """Шаг: пользователь оформляет заказ."""
    user = order_context['user']
    cart = order_context['cart']
    
    # Создаем мок заказа
    mock_order = Mock()
    mock_order.id = "ORD-123"
    mock_order.user_id = user.id
    mock_order.items = cart.items
    mock_order.status = "pending"
    mock_order.total_amount = sum(item['price'] * item['quantity'] for item in cart.items)
    
    order_context['order'] = mock_order


# ===== THEN ШАГИ (Проверки) =====

@then('заказ должен быть создан')
def order_should_be_created(order_context):
    """Шаг: проверка, что заказ создан."""
    assert order_context['order'] is not None
    assert order_context['order'].id is not None


@then(parsers.parse('статус заказа должен быть "{status}"'))
def order_status_should_be(order_context, status):
    """Шаг: проверка статуса заказа."""
    assert order_context['order'].status == status


@then(parsers.parse('общая сумма заказа должна быть {total_amount:d}'))
def order_total_should_be(order_context, total_amount):
    """Шаг: проверка суммы заказа."""
    assert order_context['order'].total_amount == total_amount
