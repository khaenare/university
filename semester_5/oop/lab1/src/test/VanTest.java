package test;

import coffee.Coffee;
import coffee.GroundCoffee;
import packaging.PackageType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import van.LoadedCoffee;
import van.Van;

import java.io.File;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class VanTest {

    private Van van;
    private final double MAX_VOLUME = 20.0; // ЗБІЛЬШИВ ОБ'ЄМ, ЩОБ УНИКНУТИ ПОМИЛОК У ТЕСТАХ

    @BeforeEach
    void setUp() {
        // Ініціалізація нового фургона перед кожним тестом
        van = new Van(MAX_VOLUME);
    }

    @Test
    void testAddCoffeeSuccess() {
        // Використовуємо Mockito для створення "фейкового" об'єкта кави
        Coffee mockCoffee = Mockito.mock(Coffee.class);

        // Налаштовуємо поведінку мока
        when(mockCoffee.getVolume()).thenReturn(1.0);
        when(mockCoffee.getName()).thenReturn("Mock Coffee");

        // Упаковка DENSE додає 0.3 л. Загальний об'єм = 1.3
        boolean result = van.addCoffee(mockCoffee, PackageType.DENSE);

        // Перевірки
        assertTrue(result, "Кава мала бути успішно додана");
        assertEquals(1.3, van.getCurrentVolume(), 0.001, "Поточний об'єм фургона пораховано неправильно");
    }

    @Test
    void testAddCoffeeOverflow() {
        Coffee mockCoffee = Mockito.mock(Coffee.class);

        // Налаштовуємо об'єм кави так, щоб він перевищував місткість фургона
        // MAX_VOLUME (20) + упаковка -> робимо каву 30.0
        when(mockCoffee.getVolume()).thenReturn(30.0);
        when(mockCoffee.getName()).thenReturn("Huge Coffee");

        boolean result = van.addCoffee(mockCoffee, PackageType.LIGHT);

        // Очікуємо false, тому що фургон переповнений
        assertFalse(result, "Метод мав повернути false через переповнення");
        assertEquals(0, van.getCurrentVolume(), "Об'єм фургона не мав змінитися");
    }

    @Test
    void testSortByPricePerKg() {
        // Створюємо реальні об'єкти для тестування сортування
        // Cheap: ціна 100, об'єм 10.0 -> ціна за літр = 10
        Coffee cheap = new GroundCoffee("Cheap", 100, 10.0);
        // Expensive: ціна 100, об'єм 1.0 -> ціна за літр = 100
        Coffee expensive = new GroundCoffee("Expensive", 100, 1.0);

        // Додаємо (тепер влазить обоє, бо MAX_VOLUME = 20)
        van.addCoffee(expensive, PackageType.LIGHT);
        van.addCoffee(cheap, PackageType.LIGHT);

        // Виконуємо сортування
        van.sortByPricePerKg();
        List<LoadedCoffee> list = van.getCoffeeList();

        // Перевіряємо порядок: перший елемент має бути дешевшим (за літр)
        assertEquals("Cheap", list.get(0).getCoffee().getName(), "Сортування працює неправильно: Cheap має бути першим");
        assertEquals("Expensive", list.get(1).getCoffee().getName(), "Сортування працює неправильно: Expensive має бути другим");
    }

    @Test
    void testSearchByPriceRange() {
        Coffee c1 = new GroundCoffee("Low Price", 50, 1.0);
        Coffee c2 = new GroundCoffee("High Price", 150, 1.0);

        van.addCoffee(c1, PackageType.LIGHT);
        van.addCoffee(c2, PackageType.LIGHT);

        // Шукаємо в діапазоні 40-60 (має знайти c1)
        List<LoadedCoffee> results = van.searchByPriceRange(40, 60);

        assertEquals(1, results.size(), "Знайдено неправильну кількість товарів");
        assertEquals("Low Price", results.get(0).getCoffee().getName());
    }

    @Test
    void testSaveAndLoadFile() {
        String testFilename = "test_data_van.txt";

        Coffee c = new GroundCoffee("File Coffee", 100, 1.0);
        van.addCoffee(c, PackageType.DENSE);

        // Зберігаємо у файл
        boolean saved = van.saveToFile(testFilename);
        assertTrue(saved, "Помилка при збереженні файлу");

        // Створюємо новий фургон і завантажуємо дані
        Van newVan = new Van(0);
        boolean loaded = newVan.loadFromFile(testFilename);

        assertTrue(loaded, "Помилка при завантаженні файлу");
        // Перевіряємо, що об'єм завантажився (20.0)
        assertEquals(20.0, newVan.getMaxVolume(), "Об'єм фургона не відновився з файлу");
        assertEquals(1, newVan.getCoffeeList().size(), "Список товарів порожній після завантаження");
        assertEquals("File Coffee", newVan.getCoffeeList().get(0).getCoffee().getName());

        // Очищення
        new File(testFilename).delete();
    }
}