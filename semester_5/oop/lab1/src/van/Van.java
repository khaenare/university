package van;

import coffee.Coffee;
import java.util.ArrayList;
import java.util.List;
import java.util.Comparator;

public class Van {
    private List<Coffee> coffeeList;

    public Van() {
        this.coffeeList = new ArrayList<>();
    }

    public void addCoffee(Coffee coffee) {
        coffeeList.add(coffee);
    }

    public void sortByPricePerKg() {
        coffeeList.sort(Comparator.comparingDouble(Coffee::getPricePerKg));
    }

    public List<Coffee> searchByPriceRange(double minPrice, double maxPrice) {
        List<Coffee> result = new ArrayList<>();
        for (Coffee coffee : coffeeList) {
            if (coffee.getPrice() >= minPrice && coffee.getPrice() <= maxPrice) {
                result.add(coffee);
            }
        }
        return result;
    }

    public void printCoffeeList() {
        for (Coffee coffee : coffeeList) {
            System.out.println(coffee);
        }
    }
}
