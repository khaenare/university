package test; // Перевір, щоб пакет співпадав з твоїм (наприклад, просто tourist або tourist.test)

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import tourist.comparator.TouristVoucherCostComparator;
import tourist.comparator.TouristVoucherDaysComparator;
import tourist.model.TouristVoucher;

import java.math.BigDecimal;

public class TouristVoucherComparatorTest {

    private TouristVoucher voucher1;
    private TouristVoucher voucher2;

    @BeforeEach
    public void setUp() {
        voucher1 = new TouristVoucher();
        voucher2 = new TouristVoucher();
    }

    @Test
    public void testCostComparator() {
        TouristVoucherCostComparator comparator = new TouristVoucherCostComparator();

        // Встановлюємо ціну напряму через BigDecimal (без класу Cost)
        voucher1.setCost(new BigDecimal("1000.00"));
        voucher2.setCost(new BigDecimal("2000.00"));

        // Перевірка: voucher1 дешевше voucher2 -> від'ємне число
        Assertions.assertTrue(comparator.compare(voucher1, voucher2) < 0,
                "Перша путівка дешевша за другу, результат має бути < 0");

        // Перевірка: voucher2 дорожче voucher1 -> додатнє число
        Assertions.assertTrue(comparator.compare(voucher2, voucher1) > 0,
                "Друга путівка дорожча за першу, результат має бути > 0");

        // Перевірка рівності
        Assertions.assertEquals(0, comparator.compare(voucher1, voucher1),
                "Ціни однакові, результат має бути 0");
    }

    @Test
    public void testDaysComparator() {
        TouristVoucherDaysComparator comparator = new TouristVoucherDaysComparator();

        // Встановлюємо кількість днів
        voucher1.setDays(5);
        voucher2.setDays(10);

        // Перевірка: 5 днів менше 10
        Assertions.assertTrue(comparator.compare(voucher1, voucher2) < 0,
                "5 днів менше ніж 10, результат має бути < 0");

        // Перевірка: 10 днів більше 5
        Assertions.assertTrue(comparator.compare(voucher2, voucher1) > 0,
                "10 днів більше ніж 5, результат має бути > 0");

        // Перевірка рівності
        Assertions.assertEquals(0, comparator.compare(voucher1, voucher1),
                "Кількість днів однакова, результат має бути 0");
    }
}