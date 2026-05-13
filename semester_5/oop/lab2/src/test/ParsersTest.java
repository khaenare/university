package test;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import tourist.model.TouristVoucher;
import tourist.parser.DomTouristVouchersParser;
import tourist.parser.SaxTouristVouchersParser;
import tourist.parser.StaxTouristVouchersParser;
import tourist.parser.TouristVouchersParser;

import java.util.List;

public class ParsersTest {

    //
    private static final String XML_PATH = "src/xml/tourist_vouchers.xml";

    @Test
    public void testDomParser() throws Exception {
        TouristVouchersParser parser = new DomTouristVouchersParser();
        List<TouristVoucher> vouchers = parser.parse(XML_PATH);

        Assertions.assertNotNull(vouchers, "Список путівок не повинен бути null");
        Assertions.assertFalse(vouchers.isEmpty(), "Список путівок не повинен бути порожнім");


        Assertions.assertEquals(4, vouchers.size(), "Кількість путівок має відповідати XML");
    }

    @Test
    public void testSaxParser() throws Exception {
        TouristVouchersParser parser = new SaxTouristVouchersParser();
        List<TouristVoucher> vouchers = parser.parse(XML_PATH);

        Assertions.assertNotNull(vouchers, "Список (SAX) не повинен бути null");
        Assertions.assertFalse(vouchers.isEmpty(), "Список (SAX) не повинен бути порожнім");


        Assertions.assertEquals(4, vouchers.size(), "Кількість путівок (SAX) має бути 4");
    }

    @Test
    public void testStaxParser() throws Exception {
        TouristVouchersParser parser = new StaxTouristVouchersParser();
        List<TouristVoucher> vouchers = parser.parse(XML_PATH);

        Assertions.assertNotNull(vouchers, "Список (StAX) не повинен бути null");
        Assertions.assertFalse(vouchers.isEmpty(), "Список (StAX) не повинен бути порожнім");


        Assertions.assertEquals(4, vouchers.size(), "Кількість путівок (StAX) має бути 4");
    }
}