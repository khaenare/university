package van;

import coffee.BeanCoffee;
import coffee.Coffee;
import coffee.GroundCoffee;
import coffee.InstantCoffee;
import packaging.PackageType;

import java.io.*;
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

    // ============================================================
// Збереження даних фургона у TXT-файл
// Формат:
// VOLUME=6.0
//
// COFFEE:
// Ground;Ground Coffee;100.0;0.5;DENSE
// ============================================================

    public boolean saveToFile(String filename) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {

            // Записуємо обʼєм фургона
            writer.println("VOLUME=" + maxVolume);
            writer.println();
            writer.println("COFFEE:");

            for (LoadedCoffee item : coffeeList) {
                Coffee c = item.getCoffee();
                PackageType pack = item.getPackageType();

                writer.println(
                        c.getTypeName() + ";" +
                                c.getName() + ";" +
                                c.getPrice() + ";" +
                                c.getVolume() + ";" +
                                pack.name()
                );
            }

            return true;

        } catch (IOException e) {
            System.out.println("Помилка збереження у файл: " + e.getMessage());
            return false;
        }
    }



// ============================================================
// Завантаження даних фургона з TXT-файлу
// ============================================================

    public boolean loadFromFile(String filename) {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {

            String line = reader.readLine();
            if (line == null || !line.startsWith("VOLUME=")) {
                System.out.println("Файл має пошкоджений формат.");
                return false;
            }

            // Зчитуємо обʼєм
            maxVolume = Double.parseDouble(line.substring(7));
            currentVolume = 0;
            coffeeList.clear();

            // Пропускаємо пустий рядок
            reader.readLine();

            // Чекаємо секцію COFFEE:
            if (!"COFFEE:".equals(reader.readLine())) {
                System.out.println("Файл має неправильну структуру.");
                return false;
            }

            // Зчитуємо всі продукти
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) continue;

                String[] parts = line.split(";");
                if (parts.length != 5) {
                    System.out.println("Неправильний рядок: " + line);
                    continue;
                }

                String type = parts[0];
                String name = parts[1];
                double price = Double.parseDouble(parts[2]);
                double volume = Double.parseDouble(parts[3]);
                PackageType pack = PackageType.valueOf(parts[4]);

                Coffee c;
                switch (type) {
                    case "Ground":
                        c = new GroundCoffee(name, price, volume);
                        break;
                    case "Instant":
                        c = new InstantCoffee(name, price, volume);
                        break;
                    case "Bean":
                        c = new BeanCoffee(name, price, volume);
                        break;
                    default:
                        System.out.println("Невідомий тип кави у файлі: " + type);
                        continue;
                }

                addCoffee(c, pack);
            }

            return true;

        } catch (IOException | NumberFormatException e) {
            System.out.println("Помилка читання файлу: " + e.getMessage());
            return false;
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
