// Базовий клас для кави
public class Coffee {
    // Поля для зберігання назви, ціни, ваги та об'єму кави
    private String name;
    private double price; // ціна за одиницю
    private double weight; // вага в кг
    private double volume; // об'єм в літрах

    // Конструктор класу
    public Coffee(String name, double price, double weight, double volume) {
        this.name = name;
        this.price = price;
        this.weight = weight;
        this.volume = volume;
    }

    // Геттери та сеттери для доступу до полів

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public double getWeight() {
        return weight;
    }

    public void setWeight(double weight) {
        this.weight = weight;
    }

    public double getVolume() {
        return volume;
    }

    public void setVolume(double volume) {
        this.volume = volume;
    }

    // Метод для обчислення співвідношення ціни та ваги (ціна за кг)
    public double getPricePerKg() {
        return price / weight;
    }

    // Метод для виведення інформації про каву
    public String toString() {
        return "Coffee{name='" + name + "', price=" + price + ", weight=" + weight + ", volume=" + volume + "}";
    }
}


// Підклас для меленого кави
class GroundCoffee extends Coffee {
    private String grindType; // тип помолу

    public GroundCoffee(String name, double price, double weight, double volume, String grindType) {
        super(name, price, weight, volume); // викликаємо конструктор батьківського класу
        this.grindType = grindType;
    }

    public String getGrindType() {
        return grindType;
    }

    public void setGrindType(String grindType) {
        this.grindType = grindType;
    }

    @Override
    public String toString() {
        return super.toString() + ", grindType='" + grindType + "'";
    }
}


// Підклас для розчинної кави
class InstantCoffee extends Coffee {
    private String packagingType; // тип упаковки (банка або пакетик)

    public InstantCoffee(String name, double price, double weight, double volume, String packagingType) {
        super(name, price, weight, volume);
        this.packagingType = packagingType;
    }

    public String getPackagingType() {
        return packagingType;
    }

    public void setPackagingType(String packagingType) {
        this.packagingType = packagingType;
    }

    @Override
    public String toString() {
        return super.toString() + ", packagingType='" + packagingType + "'";
    }
}


// Підклас для зернової кави
class BeanCoffee extends Coffee {
    private String roastLevel; // ступінь обжарки

    public BeanCoffee(String name, double price, double weight, double volume, String roastLevel) {
        super(name, price, weight, volume);
        this.roastLevel = roastLevel;
    }

    public String getRoastLevel() {
        return roastLevel;
    }

    public void setRoastLevel(String roastLevel) {
        this.roastLevel = roastLevel;
    }

    @Override
    public String toString() {
        return super.toString() + ", roastLevel='" + roastLevel + "'";
    }
}
