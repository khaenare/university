package test;

import coffee.BeanCoffee;
import coffee.Coffee;
import coffee.GroundCoffee;
import coffee.InstantCoffee;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CoffeeTest {

    @Test
    void testPricePerKgCalculation() {
        // Створюємо об'єкт кави: ціна 100, об'єм 0.5 -> ціна за літр має бути 200
        Coffee coffee = new GroundCoffee("Test Coffee", 100.0, 0.5);

        // Перевіряємо коректність розрахунку ціни за одиницю об'єму
        assertEquals(200.0, coffee.getPricePerKg(), 0.001, "Ціна за літр розрахована неправильно");
    }

    @Test
    void testSubclassCreationAndToString() {
        // Перевіряємо створення зернової кави
        BeanCoffee bean = new BeanCoffee("Arabica", 150.0, 1.0);

        // Перевіряємо, чи правильно формується рядкове представлення (toString)
        String result = bean.toString();

        // Перевіряємо наявність специфічного поля roastLevel
        assertTrue(result.contains("roastLevel"), "toString має містити інформацію про обсмаження");
        assertTrue(result.contains("Arabica"), "toString має містити назву кави");
    }

    @Test
    void testTypeNameExtraction() {
        // Перевіряємо метод getTypeName(), який обрізає слово "Coffee"
        Coffee instant = new InstantCoffee("Nescafe", 50, 0.2);

        // Очікуємо "Instant" замість "InstantCoffee"
        assertEquals("Instant", instant.getTypeName(), "Назва типу кави сформована неправильно");
    }
}