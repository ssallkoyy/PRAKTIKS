"""
Unit tests for OrderService with mocked dependencies.
Coverage: >80%
"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from order_service import OrderService, Order


class TestOrderServiceCreateOrder(unittest.TestCase):
    """Test order creation with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
        
        self.sample_items = [
            {'name': 'Laptop', 'price': 1000, 'quantity': 1},
            {'name': 'Mouse', 'price': 50, 'quantity': 2}
        ]
    
    def test_create_order_success(self):
        """Test successful order creation."""
        # Arrange
        user_id = "user123"
        items = self.sample_items
        
        # Act
        order = self.service.create_order(user_id, items)
        
        # Assert
        self.assertIsNotNone(order)
        self.assertEqual(order.user_id, user_id)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.total_amount, 1100)  # 1000 + 50*2
        
        # Verify repository was called
        self.mock_repo.save.assert_called_once_with(order)
        
        # Verify notification was sent
        self.mock_notification.send_email.assert_called_once()
        call_args = self.mock_notification.send_email.call_args
        self.assertEqual(call_args[0][0], user_id)
        self.assertIn("created", call_args[0][1])
    
    def test_create_order_with_none_user_id(self):
        """Test order creation with None user_id raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.create_order(None, self.sample_items)
        
        self.assertIn("User ID cannot be None", str(context.exception))
        
        # Verify no side effects
        self.mock_repo.save.assert_not_called()
        self.mock_notification.send_email.assert_not_called()
    
    def test_create_order_with_empty_items(self):
        """Test order creation with empty items list raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.create_order("user123", [])
        
        self.assertIn("at least one item", str(context.exception))
        
        self.mock_repo.save.assert_not_called()
    
    def test_create_order_with_none_items(self):
        """Test order creation with None items raises error."""
        with self.assertRaises((ValueError, TypeError)):
            self.service.create_order("user123", None)
    
    def test_create_order_with_zero_total(self):
        """Test order creation with zero total amount raises error."""
        items = [{'name': 'Free Item', 'price': 0, 'quantity': 1}]
        
        with self.assertRaises(ValueError) as context:
            self.service.create_order("user123", items)
        
        self.assertIn("Total amount must be positive", str(context.exception))
    
    def test_create_order_with_negative_price(self):
        """Test order creation with negative price raises error."""
        items = [{'name': 'Item', 'price': -100, 'quantity': 1}]
        
        with self.assertRaises(ValueError) as context:
            self.service.create_order("user123", items)
        
        self.assertIn("Total amount must be positive", str(context.exception))
    
    def test_create_order_calculates_total_correctly(self):
        """Test order total amount calculation."""
        items = [
            {'name': 'Item1', 'price': 10, 'quantity': 2},
            {'name': 'Item2', 'price': 20, 'quantity': 3}
        ]
        
        order = self.service.create_order("user123", items)
        
        self.assertEqual(order.total_amount, 80)  # 10*2 + 20*3
    
    def test_create_order_generates_unique_id(self):
        """Test order ID is generated."""
        order = self.service.create_order("user123", self.sample_items)
        
        self.assertIsNotNone(order.order_id)
        self.assertTrue(order.order_id.startswith("ORD-user123-"))
    
    def test_create_order_multiple_items(self):
        """Test order creation with multiple items."""
        items = [
            {'name': 'Item1', 'price': 100, 'quantity': 1},
            {'name': 'Item2', 'price': 200, 'quantity': 2},
            {'name': 'Item3', 'price': 50, 'quantity': 3}
        ]
        
        order = self.service.create_order("user123", items)
        
        self.assertEqual(order.total_amount, 650)  # 100 + 400 + 150
        self.assertEqual(len(order.items), 3)


class TestOrderServiceProcessPayment(unittest.TestCase):
    """Test payment processing with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
    
    def test_process_payment_success(self):
        """Test successful payment processing."""
        # Arrange
        order_id = "ORD-123"
        mock_order = Mock()
        mock_order.order_id = order_id
        mock_order.user_id = "user123"
        mock_order.total_amount = 500
        mock_order.status = "pending"
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_payment.process_payment.return_value = "TXN-456"
        
        # Act
        result = self.service.process_payment(order_id)
        
        # Assert
        self.assertTrue(result)
        
        # Verify payment gateway was called
        self.mock_payment.process_payment.assert_called_once_with(order_id, 500)
        
        # Verify order was updated
        self.assertEqual(mock_order.status, "paid")
        self.assertEqual(mock_order.payment_id, "TXN-456")
        self.mock_repo.update_status.assert_called_once_with(order_id, "paid")
        
        # Verify notification was sent
        self.mock_notification.send_email.assert_called_once()
    
    def test_process_payment_with_none_order_id(self):
        """Test payment processing with None order_id raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.process_payment(None)
        
        self.assertIn("Order ID cannot be None", str(context.exception))
    
    def test_process_payment_order_not_found(self):
        """Test payment processing when order not found."""
        self.mock_repo.find_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.service.process_payment("nonexistent")
        
        self.assertIn("Order not found", str(context.exception))
    
    def test_process_payment_order_not_pending(self):
        """Test payment processing when order is not in pending status."""
        mock_order = Mock()
        mock_order.status = "paid"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        with self.assertRaises(ValueError) as context:
            self.service.process_payment("ORD-123")
        
        self.assertIn("not in pending status", str(context.exception))
    
    def test_process_payment_gateway_failure(self):
        """Test payment processing when payment gateway fails."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.total_amount = 500
        mock_order.status = "pending"
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_payment.process_payment.side_effect = Exception("Gateway error")
        
        with self.assertRaises(RuntimeError) as context:
            self.service.process_payment("ORD-123")
        
        self.assertIn("Payment failed", str(context.exception))
        
        # Verify order status updated to failed
        self.assertEqual(mock_order.status, "payment_failed")
        self.mock_repo.update_status.assert_called_once_with("ORD-123", "payment_failed")
    
    def test_process_payment_notification_failure(self):
        """Test payment processing when notification fails."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.total_amount = 500
        mock_order.status = "pending"
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_payment.process_payment.return_value = "TXN-456"
        self.mock_notification.send_email.side_effect = Exception("Email failed")
        
        # Payment should still succeed even if notification fails
        result = self.service.process_payment("ORD-123")
        self.assertTrue(result)
        self.assertEqual(mock_order.status, "paid")


class TestOrderServiceCancelOrder(unittest.TestCase):
    """Test order cancellation with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
    
    def test_cancel_paid_order_with_refund(self):
        """Test cancellation of paid order with refund."""
        # Arrange
        order_id = "ORD-123"
        mock_order = Mock()
        mock_order.order_id = order_id
        mock_order.user_id = "user123"
        mock_order.status = "paid"
        mock_order.payment_id = "TXN-456"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        # Act
        result = self.service.cancel_order(order_id)
        
        # Assert
        self.assertTrue(result)
        
        # Verify refund was processed
        self.mock_payment.refund_payment.assert_called_once_with("TXN-456")
        
        # Verify order status updated
        self.assertEqual(mock_order.status, "cancelled")
        self.mock_repo.update_status.assert_called_once_with(order_id, "cancelled")
        
        # Verify notification sent
        self.mock_notification.send_email.assert_called_once()
    
    def test_cancel_pending_order_no_refund(self):
        """Test cancellation of pending order (no refund needed)."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.status = "pending"
        mock_order.payment_id = None
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        result = self.service.cancel_order("ORD-123")
        
        self.assertTrue(result)
        
        # Verify no refund was attempted
        self.mock_payment.refund_payment.assert_not_called()
        
        # Verify order status updated
        self.assertEqual(mock_order.status, "cancelled")
    
    def test_cancel_order_with_none_id(self):
        """Test cancellation with None order_id raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.cancel_order(None)
        
        self.assertIn("Order ID cannot be None", str(context.exception))
    
    def test_cancel_order_not_found(self):
        """Test cancellation when order not found."""
        self.mock_repo.find_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.service.cancel_order("nonexistent")
        
        self.assertIn("Order not found", str(context.exception))
    
    def test_cancel_already_cancelled_order(self):
        """Test cancellation of already cancelled order."""
        mock_order = Mock()
        mock_order.status = "cancelled"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        with self.assertRaises(ValueError) as context:
            self.service.cancel_order("ORD-123")
        
        self.assertIn("already cancelled", str(context.exception))
    
    def test_cancel_order_refund_failure(self):
        """Test cancellation when refund fails."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.status = "paid"
        mock_order.payment_id = "TXN-456"
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_payment.refund_payment.side_effect = Exception("Refund failed")
        
        with self.assertRaises(RuntimeError) as context:
            self.service.cancel_order("ORD-123")
        
        self.assertIn("Refund failed", str(context.exception))
    
    def test_cancel_order_notification_failure(self):
        """Test cancellation when notification fails."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.status = "pending"
        mock_order.payment_id = None
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_notification.send_email.side_effect = Exception("Email failed")
        
        # Cancellation should still succeed
        result = self.service.cancel_order("ORD-123")
        self.assertTrue(result)
        self.assertEqual(mock_order.status, "cancelled")


class TestOrderServiceGetUserOrders(unittest.TestCase):
    """Test getting user orders with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
    
    def test_get_user_orders_success(self):
        """Test successful retrieval of user orders."""
        # Arrange
        user_id = "user123"
        mock_orders = [Mock(), Mock(), Mock()]
        self.mock_repo.find_by_user_id.return_value = mock_orders
        
        # Act
        orders = self.service.get_user_orders(user_id)
        
        # Assert
        self.assertEqual(len(orders), 3)
        self.mock_repo.find_by_user_id.assert_called_once_with(user_id)
    
    def test_get_user_orders_with_none_id(self):
        """Test getting orders with None user_id raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.get_user_orders(None)
        
        self.assertIn("User ID cannot be None", str(context.exception))
    
    def test_get_user_orders_empty_list(self):
        """Test getting orders returns empty list for user with no orders."""
        self.mock_repo.find_by_user_id.return_value = []
        
        orders = self.service.get_user_orders("user123")
        
        self.assertEqual(len(orders), 0)


class TestOrderServiceGetOrderStatus(unittest.TestCase):
    """Test getting order status with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
    
    def test_get_order_status_success(self):
        """Test successful retrieval of order status."""
        mock_order = Mock()
        mock_order.status = "paid"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        status = self.service.get_order_status("ORD-123")
        
        self.assertEqual(status, "paid")
        self.mock_repo.find_by_id.assert_called_once_with("ORD-123")
    
    def test_get_order_status_with_none_id(self):
        """Test getting status with None order_id raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.get_order_status(None)
        
        self.assertIn("Order ID cannot be None", str(context.exception))
    
    def test_get_order_status_not_found(self):
        """Test getting status when order not found."""
        self.mock_repo.find_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.service.get_order_status("nonexistent")
        
        self.assertIn("Order not found", str(context.exception))
    
    def test_get_order_status_pending(self):
        """Test getting pending order status."""
        mock_order = Mock()
        mock_order.status = "pending"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        status = self.service.get_order_status("ORD-123")
        self.assertEqual(status, "pending")
    
    def test_get_order_status_cancelled(self):
        """Test getting cancelled order status."""
        mock_order = Mock()
        mock_order.status = "cancelled"
        
        self.mock_repo.find_by_id.return_value = mock_order
        
        status = self.service.get_order_status("ORD-123")
        self.assertEqual(status, "cancelled")


class TestOrderServiceEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_repo = Mock()
        self.mock_notification = Mock()
        self.mock_payment = Mock()
        
        self.service = OrderService(
            self.mock_repo,
            self.mock_notification,
            self.mock_payment
        )
    
    def test_create_order_with_large_quantity(self):
        """Test order creation with large quantity."""
        items = [{'name': 'Item', 'price': 10, 'quantity': 1000000}]
        
        order = self.service.create_order("user123", items)
        
        self.assertEqual(order.total_amount, 10000000)
    
    def test_create_order_with_decimal_prices(self):
        """Test order creation with decimal prices."""
        items = [{'name': 'Item', 'price': 19.99, 'quantity': 3}]
        
        order = self.service.create_order("user123", items)
        
        self.assertAlmostEqual(order.total_amount, 59.97, places=2)
    
    def test_create_order_with_many_items(self):
        """Test order creation with many items."""
        items = [{'name': 'Item{}'.format(i), 'price': 10, 'quantity': 1} 
                 for i in range(100)]
        
        order = self.service.create_order("user123", items)
        
        self.assertEqual(order.total_amount, 1000)
        self.assertEqual(len(order.items), 100)
    
    def test_process_payment_with_very_large_amount(self):
        """Test payment processing with very large amount."""
        mock_order = Mock()
        mock_order.order_id = "ORD-123"
        mock_order.user_id = "user123"
        mock_order.total_amount = 1000000.50
        mock_order.status = "pending"
        
        self.mock_repo.find_by_id.return_value = mock_order
        self.mock_payment.process_payment.return_value = "TXN-456"
        
        result = self.service.process_payment("ORD-123")
        
        self.assertTrue(result)
        self.mock_payment.process_payment.assert_called_once_with("ORD-123", 1000000.50)
    
    def test_multiple_operations_sequential(self):
        """Test multiple operations in sequence."""
        # Create order
        items = [{'name': 'Item', 'price': 100, 'quantity': 1}]
        order = self.service.create_order("user123", items)
        
        # Process payment
        order.status = "pending"
        self.mock_repo.find_by_id.return_value = order
        self.mock_payment.process_payment.return_value = "TXN-123"
        
        self.service.process_payment(order.order_id)
        
        # Cancel order
        order.status = "paid"
        order.payment_id = "TXN-123"
        self.service.cancel_order(order.order_id)
        
        self.assertEqual(order.status, "cancelled")
        self.mock_payment.refund_payment.assert_called_once_with("TXN-123")


def run_tests():
    """Run all tests and display results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceCreateOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceProcessPayment))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceCancelOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceGetUserOrders))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceGetOrderStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderServiceEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST COVERAGE SUMMARY")
    print("=" * 70)
    print("Tests run: {}".format(result.testsRun))
    print("Failures: {}".format(len(result.failures)))
    print("Errors: {}".format(len(result.errors)))
    print("Success: {}".format(result.wasSuccessful()))
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
