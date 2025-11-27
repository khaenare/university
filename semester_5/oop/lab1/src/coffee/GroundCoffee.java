package coffee;

public class GroundCoffee extends Coffee {
    private String grindType;

    public GroundCoffee(String name, double price, double weight, double volume, String grindType) {
        super(name, price, weight, volume);
        this.grindType = grindType;
    }

    public String getGrindType() {
        return grindType;
    }

    @Override
    public String toString() {
        return super.toString() + ", grindType='" + grindType + "'";
    }
}
