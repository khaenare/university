package van;

import coffee.Coffee;
import packaging.PackageType;

import java.util.ArrayList;
import java.util.List;
import java.util.Comparator;

public class Van {
    private List<LoadedCoffee> coffeeList; // Список кави в фургоні
    private double maxVolume; // Максимальний об'єм фургона
    private double currentVolume; // Поточний об'єм, зайнятий кавою

    // Конструктор
    public Van(double maxVolume) {
        this.coffeeList = new ArrayList<>();

        this.maxVolume = maxVolume;
        this.currentVolume = 0;
    }

    public boolean addCoffee(Coffee coffee, PackageType pack) {

        double totalVolume = coffee.getVolume() + pack.getVolume();

        if (currentVolume + totalVolume <= maxVolume) {
            coffeeList.add(new LoadedCoffee(coffee, pack)); // зберігаємо разом
            currentVolume += totalVolume;
            return true;
        } else {
            System.out.println("Фургон переповнений! Недостатньо місця для " + coffee.getName());
            return false;
        }
    }



    // Метод для сортування кави за ціною за літр
    public void sortByPricePerKg() {
        coffeeList.sort(
                Comparator.comparingDouble(item -> item.getCoffee().getPricePerKg())
        );

    }

    // Метод для пошуку кави по діапазону ціни
    public List<LoadedCoffee> searchByPriceRange(double minPrice, double maxPrice) {
        List<LoadedCoffee> result = new ArrayList<>();

        for (LoadedCoffee item : coffeeList) {
            Coffee coffee = item.getCoffee();
            if (coffee.getPrice() >= minPrice && coffee.getPrice() <= maxPrice) {
                result.add(item);
            }
        }
        return result;
    }


    // Метод для виведення всіх кав у фургоні
    public void printCoffeeList() {
        if (coffeeList.isEmpty()) {
            System.out.println("Фургон порожній.");
        } else {
            for (LoadedCoffee item : coffeeList) {
                System.out.println(item);
            }
        }
    }


    // Геттери та сеттери
    public double getMaxVolume() {
        return maxVolume;
    }

    public double getCurrentVolume() {
        return currentVolume;
    }
}
