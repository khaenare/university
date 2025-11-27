import java.util.ArrayList;
import java.util.List;
import java.util.Comparator;

// Клас для фургона, що зберігає каву
class Van {
    private List<Coffee> coffeeList; // список кави в фургоні

    // Конструктор
    public Van() {
        this.coffeeList = new ArrayList<>();
    }

    // Метод для додавання кави в фургон
    public void addCoffee(Coffee coffee) {
        coffeeList.add(coffee);
    }

    // Метод для сортування кави за ціною за кг
    public void sortByPricePerKg() {
        coffeeList.sort(Comparator.comparingDouble(Coffee::getPricePerKg));
    }

    // Метод для пошуку кави в діапазоні ціни
    public List<Coffee> searchByPriceRange(double minPrice, double maxPrice) {
        List<Coffee> result = new ArrayList<>();
        for (Coffee coffee : coffeeList) {
            if (coffee.getPrice() >= minPrice && coffee.getPrice() <= maxPrice) {
                result.add(coffee);
            }
        }
        return result;
    }

    // Метод для виведення списку кави у фургоні
    public void printCoffeeList() {
        for (Coffee coffee : coffeeList) {
            System.out.println(coffee);
        }
    }
}
