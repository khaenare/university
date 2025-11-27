import java.util.List;
import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        // Створення різних типів кави
        Coffee groundCoffee = new GroundCoffee("Ground Coffee", 100.0, 1.0, 0.5, "Fine");
        Coffee instantCoffee = new InstantCoffee("Instant Coffee", 120.0, 0.8, 0.4, "Can");
        Coffee beanCoffee = new BeanCoffee("Bean Coffee", 150.0, 1.2, 0.6, "Medium Roast");

        // Створення упаковок
        Package groundCoffeePackage = new Package("Bag", 0.2);
        Package instantCoffeePackage = new Package("Can", 0.15);
        Package beanCoffeePackage = new Package("Box", 0.25);

        // Створення фургона і додавання кави
        Van coffeeVan = new Van();
        coffeeVan.addCoffee(groundCoffee);
        coffeeVan.addCoffee(instantCoffee);
        coffeeVan.addCoffee(beanCoffee);

        // Сортування і виведення кави
        System.out.println("Coffee list sorted by price per kg:");
        coffeeVan.sortByPricePerKg();
        coffeeVan.printCoffeeList();

        // Пошук кави в діапазоні цін
        System.out.println("\nSearching for coffee in the price range of 100 to 130:");
        List<Coffee> foundCoffee = coffeeVan.searchByPriceRange(100, 130);
        for (Coffee coffee : foundCoffee) {
            System.out.println(coffee);
        }
    }
}
