package coffee;

public class Coffee {
    private String name; // Назва кави
    private double price; // Ціна кави
    private double volume; // Об'єм кави

    // Конструктор для ініціалізації кави
    public Coffee(String name, double price, double volume) {
        this.name = name;
        this.price = price;
        this.volume = volume;
    }

    // Геттери
    public String getName() {
        return name;
    }

    // Повертає тип кави як текст (для збереження у файл)
    public String getTypeName() {
        return this.getClass().getSimpleName().replace("Coffee", "");
    }


    public double getPrice() {
        return price;
    }

    public double getVolume() {
        return volume;
    }

    // Метод для обчислення ціни за літр (замість ціни за кг)
    public double getPricePerKg() {
        return price / volume; // Ціна за літр
    }

    // Метод для виведення інформації про каву
    @Override
    public String toString() {
        return "Coffee{name='" + name + "', price=" + price + ", volume=" + volume + "}";
    }
}
