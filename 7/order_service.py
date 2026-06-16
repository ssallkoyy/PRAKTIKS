"""
Order Service - handles order processing in e-commerce.
Has dependencies on external services (repository, notifications, payment).
"""
from datetime import datetime


class Order:
    """Order entity."""
    
    def __init__(self, order_id, user_id, items, total_amount):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.total_amount = total_amount
        self.status = "pending"
        self.created_at = datetime.now()
        self.payment_id = None


class OrderRepository:
    """Repository for order persistence (database)."""
    
    def save(self, order):
        """Save order to database."""
        raise NotImplementedError
    
    def find_by_id(self, order_id):
        """Find order by ID."""
        raise NotImplementedError
    
    def find_by_user_id(self, user_id):
        """Find all orders for user."""
        raise NotImplementedError
    
    def update_status(self, order_id, status):
        """Update order status."""
        raise NotImplementedError


class NotificationService:
    """Service for sending notifications."""
    
    def send_email(self, user_id, message):
        """Send email notification."""
        raise NotImplementedError
    
    def send_sms(self, user_id, message):
        """Send SMS notification."""
        raise NotImplementedError


class PaymentGateway:
    """External payment gateway."""
    
    def process_payment(self, order_id, amount):
        """Process payment and return transaction ID."""
        raise NotImplementedError
    
    def refund_payment(self, transaction_id):
        """Refund payment."""
        raise NotImplementedError


class OrderService:
    """
    Service for managing orders.
    Dependencies: OrderRepository, NotificationService, PaymentGateway
    """
    
    def __init__(self, order_repo, notification_service, payment_gateway):
        """
        Initialize OrderService with dependencies.
        
        Args:
            order_repo: OrderRepository instance
            notification_service: NotificationService instance
            payment_gateway: PaymentGateway instance
        """
        self.order_repo = order_repo
        self.notification_service = notification_service
        self.payment_gateway = payment_gateway
    
    def create_order(self, user_id, items):
        """
        Create a new order.
        
        Args:
            user_id: User ID
            items: List of items (dict with 'name', 'price', 'quantity')
            
        Returns:
            Order: Created order
            
        Raises:
            ValueError: If user_id is None or items is empty
        """
        if user_id is None:
            raise ValueError("User ID cannot be None")
        
        if not items or len(items) == 0:
            raise ValueError("Order must contain at least one item")
        
        # Calculate total amount
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        
        # Generate order ID
        order_id = "ORD-{}-{}".format(user_id, datetime.now().timestamp())
        
        # Create order
        order = Order(order_id, user_id, items, total_amount)
        
        # Save to repository
        self.order_repo.save(order)
        
        # Send notification
        self.notification_service.send_email(
            user_id, 
            "Your order {} has been created".format(order_id)
        )
        
        return order
    
    def process_payment(self, order_id):
        """
        Process payment for order.
        
        Args:
            order_id: Order ID
            
        Returns:
            bool: True if payment successful
            
        Raises:
            ValueError: If order not found
            RuntimeError: If payment fails
        """
        if order_id is None:
            raise ValueError("Order ID cannot be None")
        
        # Find order
        order = self.order_repo.find_by_id(order_id)
        
        if order is None:
            raise ValueError("Order not found: {}".format(order_id))
        
        if order.status != "pending":
            raise ValueError("Order is not in pending status")
        
        # Process payment
        try:
            transaction_id = self.payment_gateway.process_payment(
                order_id, 
                order.total_amount
            )
            
            # Update order with payment info
            order.payment_id = transaction_id
            order.status = "paid"
            self.order_repo.update_status(order_id, "paid")
            
            # Send confirmation
            self.notification_service.send_email(
                order.user_id,
                "Payment successful for order {}".format(order_id)
            )
            
            return True
            
        except Exception as e:
            order.status = "payment_failed"
            self.order_repo.update_status(order_id, "payment_failed")
            raise RuntimeError("Payment failed: {}".format(str(e)))
    
    def cancel_order(self, order_id):
        """
        Cancel order and refund payment.
        
        Args:
            order_id: Order ID
            
        Returns:
            bool: True if cancellation successful
            
        Raises:
            ValueError: If order not found
            RuntimeError: If refund fails
        """
        if order_id is None:
            raise ValueError("Order ID cannot be None")
        
        # Find order
        order = self.order_repo.find_by_id(order_id)
        
        if order is None:
            raise ValueError("Order not found: {}".format(order_id))
        
        if order.status == "cancelled":
            raise ValueError("Order is already cancelled")
        
        # Refund payment if order was paid
        if order.status == "paid" and order.payment_id:
            try:
                self.payment_gateway.refund_payment(order.payment_id)
            except Exception as e:
                raise RuntimeError("Refund failed: {}".format(str(e)))
        
        # Update order status
        order.status = "cancelled"
        self.order_repo.update_status(order_id, "cancelled")
        
        # Send notification
        self.notification_service.send_email(
            order.user_id,
            "Your order {} has been cancelled".format(order_id)
        )
        
        return True
    
    def get_user_orders(self, user_id):
        """
        Get all orders for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of orders
            
        Raises:
            ValueError: If user_id is None
        """
        if user_id is None:
            raise ValueError("User ID cannot be None")
        
        return self.order_repo.find_by_user_id(user_id)
    
    def get_order_status(self, order_id):
        """
        Get order status.
        
        Args:
            order_id: Order ID
            
        Returns:
            str: Order status
            
        Raises:
            ValueError: If order not found
        """
        if order_id is None:
            raise ValueError("Order ID cannot be None")
        
        order = self.order_repo.find_by_id(order_id)
        
        if order is None:
            raise ValueError("Order not found: {}".format(order_id))
        
        return order.status
