package main;


import coffee.*;
import packaging.PackageType;
import van.LoadedCoffee;
import van.Van;

import java.util.Scanner;
import java.util.List;


public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Запит на вибір між демонстрацією та інтерактивним меню
        System.out.println("Виберіть опцію:");
        System.out.println("1. Демонстрація з попередньо заповненими даними");
        System.out.println("2. Інтерактивне меню");

        int choice = scanner.nextInt();
        scanner.nextLine(); // Зчитуємо символ нового рядка після введення числа

        if (choice == 1) {
            // Демонстраційний режим
            runDemo(scanner);
        } else if (choice == 2) {
            // Інтерактивне меню
            interactiveMenu(scanner);
        } else {
            System.out.println("Невірний вибір. Завершення програми.");
        }
    }

    private static double askDouble(Scanner scanner, String message) {
        System.out.println(message);
        while (!scanner.hasNextDouble()) {
            System.out.println("Помилка: введіть число!");
            scanner.nextLine();
        }
        double value = scanner.nextDouble();
        scanner.nextLine();
        return value;
    }


    // Демонстраційний режим
    private static void runDemo(Scanner scanner) {

        // Запит на об'єм фургона
        System.out.println("Введіть об'єм фургона для демонстрації:");
        double maxVolume = scanner.nextDouble();
        scanner.nextLine();

        System.out.println("Обʼєм фургона встановлено: " + maxVolume + " л");

        // Створення фургона
        Van coffeeVan = new Van(maxVolume);

        System.out.println("\nДемонстрація з попередньо заповненими даними...");

        Coffee groundCoffee = new GroundCoffee("Ground Coffee", 100.0, 0.5);
        Coffee instantCoffee = new InstantCoffee("Instant Coffee", 120.0, 0.4);
        Coffee beanCoffee = new BeanCoffee("Bean Coffee", 150.0, 0.6);

        // Додавання кави
        coffeeVan.addCoffee(groundCoffee, PackageType.DENSE);
        coffeeVan.addCoffee(instantCoffee, PackageType.LIGHT);
        coffeeVan.addCoffee(beanCoffee, PackageType.DENSE);

        // Виведення початкового списку
        System.out.println("\nПочатковий список кави:");
        coffeeVan.printCoffeeList();

        // Сортування
        System.out.println("\nСписок кави, відсортований за ціною за літр:");
        coffeeVan.sortByPricePerKg();
        coffeeVan.printCoffeeList();

        // Пошук
        System.out.println("\nПошук кави в діапазоні 100 - 130:");
        List<LoadedCoffee> found = coffeeVan.searchByPriceRange(100, 130);
        for (LoadedCoffee item : found) {
            System.out.println(item);
        }

        // Перевантаження
        System.out.println("\nСпробуємо додати каву, щоб перевантажити фургон:");

        Coffee extra = new GroundCoffee("Extra Coffee", 80.0, 4.5); // великий обʼєм
        boolean added = coffeeVan.addCoffee(extra, PackageType.DENSE);

        if (!added) {
            System.out.println("Фургон переповнений! Стан фургона після невдалої спроби додавання:");
            coffeeVan.printCoffeeList();
        } else {
            System.out.println("Помилка: мала статись відмова через переповнення, але кава була додана!");
        }


        System.out.println("\nДемонстрація завершена.\n");
    }


    // Інтерактивне меню
    private static void interactiveMenu(Scanner scanner) {
        System.out.println("\nІнтерактивне меню:");

        // Запит на об'єм фургона
        System.out.println("Введіть об'єм фургона:");
        double maxVolume = scanner.nextDouble();
        Van coffeeVan = new Van(maxVolume);

        while (true) {
            System.out.println("\nОберіть дію:");
            System.out.println("1. Додати каву в фургон");
            System.out.println("2. Сортувати каву за ціною за літр");
            System.out.println("3. Пошук кави за ціною");
            System.out.println("4. Вивести всі товари в фургоні");
            System.out.println("5. Вихід");

            int choice = scanner.nextInt();
            scanner.nextLine(); // Зчитуємо символ нового рядка

            switch (choice) {
                case 1:
                    addCoffeeToVan(scanner, coffeeVan);
                    break;
                case 2:
                    coffeeVan.sortByPricePerKg();
                    coffeeVan.printCoffeeList();
                    break;
                case 3:
                    searchCoffeeByPrice(scanner, coffeeVan);
                    break;
                case 4:
                    coffeeVan.printCoffeeList();
                    break;
                case 5:
                    System.out.println("Завершення програми.");
                    return;
                default:
                    System.out.println("Невірний вибір. Спробуйте ще раз.");
            }
        }
    }

    // Метод для додавання кави в фургон
    private static void addCoffeeToVan(Scanner scanner, Van van) {
        System.out.println("Введіть назву кави:");
        String name = scanner.nextLine();

        double price = askDouble(scanner, "Введіть ціну кави:");

        double volume = askDouble(scanner, "Введіть обʼєм кави:");

        String type;
        while (true) {
            System.out.println("Введіть тип кави (Ground, Instant, Bean):");
            type = scanner.nextLine();

            if (type.equalsIgnoreCase("Ground")
                    || type.equalsIgnoreCase("Instant")
                    || type.equalsIgnoreCase("Bean")) {
                break;
            }
            System.out.println("Невірний тип кави! Спробуйте ще раз.");
        }

        // Вибір упаковки з валідацією
        PackageType pack = null;

        while (pack == null) {
            System.out.println("Оберіть упаковку (DENSE або LIGHT):");
            String input = scanner.nextLine().trim().toUpperCase();

            if (input.equals("DENSE")) {
                pack = PackageType.DENSE;
            } else if (input.equals("LIGHT")) {
                pack = PackageType.LIGHT;
            } else {
                System.out.println("Невірний тип упаковки! Спробуйте ще раз.");
            }
        }


        Coffee coffee;

        if (type.equalsIgnoreCase("Ground")) {
            coffee = new GroundCoffee(name, price, volume);
        } else if (type.equalsIgnoreCase("Instant")) {
            coffee = new InstantCoffee(name, price, volume);
        } else {
            coffee = new BeanCoffee(name, price, volume);
        }

        if (van.addCoffee(coffee, pack)) {
            System.out.println("Каву додано!");
        }
    }


    // Метод для пошуку кави за ціною
    private static void searchCoffeeByPrice(Scanner scanner, Van coffeeVan) {
        System.out.println("Введіть мінімальну ціну:");
        double minPrice = scanner.nextDouble();

        System.out.println("Введіть максимальну ціну:");
        double maxPrice = scanner.nextDouble();

        List<LoadedCoffee> foundCoffee = coffeeVan.searchByPriceRange(minPrice, maxPrice);

        if (foundCoffee.isEmpty()) {
            System.out.println("Не знайдено кави в заданому діапазоні.");
        } else {
            for (LoadedCoffee item : foundCoffee) {
                System.out.println(item); // Вывод кофе + упаковки
            }
        }

    }
}

