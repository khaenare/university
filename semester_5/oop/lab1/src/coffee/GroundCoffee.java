package coffee;

// Підклас для меленої кави
public class GroundCoffee extends Coffee {
    private String grindType; // Тип помолу

    public GroundCoffee(String name, double price, double volume) {
        super(name, price, volume);
        this.grindType = "Fine"; // Значення за замовчуванням
    }

    @Override
    public String toString() {
        return super.toString() + ", grindType='" + grindType + "'";
    }
}
