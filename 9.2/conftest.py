"""
Фикстуры для тестов заказа.
Содержит общие данные и моки для всех тестов.
"""
import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_order_service():
    """Создает мок сервиса заказов."""
    service = Mock()
    return service


@pytest.fixture
def mock_user():
    """Создает мок пользователя."""
    user = Mock()
    user.id = "user123"
    user.is_authenticated = True
    return user


@pytest.fixture
def mock_cart():
    """Создает мок корзины."""
    cart = Mock()
    cart.items = []
    cart.is_empty = False
    return cart


@pytest.fixture
def order_context():
    """Контекст для передачи данных между шагами."""
    return {
        'user': None,
        'cart': None,
        'order': None,
        'error': None
    }
