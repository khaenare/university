package test;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import tourist.model.TouristVoucher;
import tourist.model.TransportType;
import tourist.model.VoucherType;

import java.math.BigDecimal;

public class TouristVoucherTest {

    @Test
    public void testTouristVoucherCreation() {
        // Створення об'єкта
        TouristVoucher voucher = new TouristVoucher();

        // Тестові дані
        String id = "test1";
        VoucherType type = VoucherType.REST;
        TransportType transport = TransportType.BUS;
        BigDecimal cost = new BigDecimal("500.00");
        String country = "Ukraine";

        // Встановлення значень (тестуємо сеттери)
        voucher.setId(id);
        voucher.setType(type);
        voucher.setTransport(transport);
        voucher.setCost(cost);
        voucher.setCountry(country);
        voucher.setDays(10);

        // Перевірка значень (тестуємо геттери)
        Assertions.assertEquals(id, voucher.getId(), "ID повинен співпадати");
        Assertions.assertEquals(type, voucher.getType(), "Тип повинен співпадати");
        Assertions.assertEquals(transport, voucher.getTransport(), "Транспорт повинен співпадати");
        Assertions.assertEquals(cost, voucher.getCost(), "Вартість повинна співпадати");
        Assertions.assertEquals("Ukraine", voucher.getCountry(), "Країна повинна співпадати");

        // Перевірка методу toString (щоб він не падав)
        Assertions.assertNotNull(voucher.toString(), "toString не повинен повертати null");
    }
}