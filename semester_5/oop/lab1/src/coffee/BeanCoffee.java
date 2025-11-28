package coffee;

// Підклас для зернової кави
public class BeanCoffee extends Coffee {
    private String roastLevel; // Рівень обсмаження

    public BeanCoffee(String name, double price, double volume) {
        super(name, price, volume);
        this.roastLevel = "Medium Roast"; // Значення за замовчуванням
    }

    @Override
    public String toString() {
        return super.toString() + ", roastLevel='" + roastLevel + "'";
    }
}

