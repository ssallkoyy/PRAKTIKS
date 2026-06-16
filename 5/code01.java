// ПОЛНОСТЬЮ ПЛОХОЙ КОД - ЗАДАЧА ДЛЯ РЕФАКТОРИНГА
import java.util.*;

public class Shop {

    private List items = new ArrayList();
    private String n;
    private double p;
    private int q;
    private String c;
    
    public void addItem(String n, double p, int q, String c) {
        this.n = n;
        this.p = p;
        this.q = q;
        this.c = c;
        items.add(n + ":" + p + ":" + q + ":" + c);
        System.out.println("Item added: " + n);
    }
    
    public double calcTotal() {
        double t = 0;
        for (int i = 0; i < items.size(); i++) {
            String item = (String) items.get(i);
            String[] parts = item.split(":");
            double price = Double.parseDouble(parts[1]);
            int quantity = Integer.parseInt(parts[2]);
            t = t + (price * quantity);
        }
        
        if (t > 100) {
            t = t * 0.9;
            System.out.println("Discount 10% applied!");
        } else if (t > 50) {
            t = t * 0.95;
            System.out.println("Discount 5% applied!");
        }
        
        return t;
    }
    
    public void processOrder(String customerName, String customerEmail, String customerPhone, 
                             String shippingAddress, String paymentMethod, String promoCode) {
        
        System.out.println("Processing order for: " + customerName);
        System.out.println("Email: " + customerEmail);
        System.out.println("Phone: " + customerPhone);
        System.out.println("Address: " + shippingAddress);
        System.out.println("Payment: " + paymentMethod);
        
        double total = calcTotal();
        
        if (promoCode != null && !promoCode.isEmpty()) {
            if (promoCode.equals("SAVE10")) {
                total = total * 0.9;
                System.out.println("Promo code applied: 10% off");
            } else if (promoCode.equals("SAVE5")) {
                total = total - 5;
                System.out.println("Promo code applied: $5 off");
            } else {
                System.out.println("Invalid promo code");
            }
        }
        
        System.out.println("Final total: $" + total);
        
        // Save to database simulation
        System.out.println("INSERT INTO orders (customer, total) VALUES ('" + customerName + "', " + total + ")");
        
        // Send email
        System.out.println("Sending email to " + customerEmail + ": Your order total is $" + total);
        
        // Send SMS
        if (customerPhone != null) {
            System.out.println("Sending SMS to " + customerPhone + ": Order confirmed");
        }
        
        // Log
        System.out.println("Order processed at " + new Date());
    }
    
    public void generateReport() {
        System.out.println("=== SALES REPORT ===");
        double totalSales = 0;
        for (int i = 0; i < items.size(); i++) {
            String item = (String) items.get(i);
            String[] parts = item.split(":");
            String name = parts[0];
            double price = Double.parseDouble(parts[1]);
            int quantity = Integer.parseInt(parts[2]);
            double itemTotal = price * quantity;
            totalSales = totalSales + itemTotal;
            System.out.println(name + " x " + quantity + " = $" + itemTotal);
        }
        System.out.println("TOTAL SALES: $" + totalSales);
    }
    
    public static void main(String[] args) {
        Shop shop = new Shop();
        shop.addItem("Laptop", 999.99, 1, "Electronics");
        shop.addItem("Mouse", 25.50, 2, "Electronics");
        shop.addItem("Notebook", 3.99, 5, "Stationery");
        
        shop.processOrder("John Doe", "john@mail.com", "1234567890", 
                         "123 Main St", "Credit Card", "SAVE10");
        
        shop.generateReport();
    }
}