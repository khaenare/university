package coffee;

public class BeanCoffee extends Coffee {
    private String roastLevel;

    public BeanCoffee(String name, double price, double weight, double volume, String roastLevel) {
        super(name, price, weight, volume);
        this.roastLevel = roastLevel;
    }

    public String getRoastLevel() {
        return roastLevel;
    }

    @Override
    public String toString() {
        return super.toString() + ", roastLevel='" + roastLevel + "'";
    }
}
