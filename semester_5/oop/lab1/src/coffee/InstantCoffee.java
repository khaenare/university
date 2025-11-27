package coffee;

public class InstantCoffee extends Coffee {
    private String packagingType;

    public InstantCoffee(String name, double price, double weight, double volume, String packagingType) {
        super(name, price, weight, volume);
        this.packagingType = packagingType;
    }

    public String getPackagingType() {
        return packagingType;
    }

    @Override
    public String toString() {
        return super.toString() + ", packagingType='" + packagingType + "'";
    }
}
