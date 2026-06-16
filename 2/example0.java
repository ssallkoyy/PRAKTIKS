java
// ПЛОХОЙ КОД - НАРУШЕНИЕ SRP, OCP, DIP
import java.util.*;

class Order {
    String customerEmail;
    double amount;
    List<String> items;
    
    public Order(String customerEmail, double amount, List<String> items) {
        this.customerEmail = customerEmail;
        this.amount = amount;
        this.items = items;
    }
}

class OrderProcessor {
    
    public void processOrder(Order order) {
        // 1. Валидация заказа
        if (order.amount <= 0) {
            throw new IllegalArgumentException("Сумма должна быть положительной");
        }
        if (order.customerEmail == null || !order.customerEmail.contains("@")) {
            throw new IllegalArgumentException("Некорректный email");
        }
        
        // 2. Расчет скидки
        double discount = 0;
        if (order.amount > 1000) {
            discount = 0.1; // 10% скидка
        } else if (order.amount > 500) {
            discount = 0.05; // 5% скидка
        }
        double finalAmount = order.amount * (1 - discount);
        
        // 3. Сохранение в базу данных (симуляция)
        System.out.println("INSERT INTO orders (email, amount) VALUES ('" + order.customerEmail + "', " + finalAmount + ")");
        
        // 4. Отправка email
        System.out.println("Отправка email на " + order.customerEmail + ": Ваш заказ на сумму " + finalAmount + " принят!");
        
        // 5. Логирование
        System.out.println("Лог: Заказ обработан для " + order.customerEmail);
    }
}

// Код для тестирования
public class Main {
    public static void main(String[] args) {
        Order order = new Order("test@mail.com", 1500, Arrays.asList("Товар1", "Товар2"));
        OrderProcessor processor = new OrderProcessor();
        processor.processOrder(order);
    }
}
