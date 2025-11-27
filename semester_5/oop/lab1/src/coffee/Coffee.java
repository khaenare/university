package coffee;

public class Coffee {
    private String name;
    private double price;
    private double weight;
    private double volume;

    public Coffee(String name, double price, double weight, double volume) {
        this.name = name;
        this.price = price;
        this.weight = weight;
        this.volume = volume;
    }

    public String getName() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    public double getWeight() {
        return weight;
    }

    public double getVolume() {
        return volume;
    }

    public double getPricePerKg() {
        return price / weight;
    }

    @Override
    public String toString() {
        return "Coffee{name='" + name + "', price=" + price + ", weight=" + weight + ", volume=" + volume + "}";
    }
}
