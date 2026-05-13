package tourist.test;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import tourist.util.XmlValidator;

import java.io.File;

public class XmlValidatorTest {

    // Шляхи до файлів (якщо папка xml лежить у src)
    private static final String XSD_PATH = "src/xml/tourist_vouchers.xsd";
    private static final String XML_PATH = "src/xml/tourist_vouchers.xml";

    // Шлях до неіснуючого файлу
    private static final String WRONG_XML_PATH = "src/xml/non_existent.xml";

    @Test
    public void testValidateCorrectXml() {
        // Перевіряємо наявність файлів перед тестом
        File xmlFile = new File(XML_PATH);
        File xsdFile = new File(XSD_PATH);

        Assertions.assertTrue(xmlFile.exists(), "Файл XML має існувати: " + xmlFile.getAbsolutePath());
        Assertions.assertTrue(xsdFile.exists(), "Файл XSD має існувати: " + xsdFile.getAbsolutePath());

        // ! ВИПРАВЛЕННЯ: Створюємо об'єкт, бо метод validate не статичний !
        XmlValidator validator = new XmlValidator();
        boolean isValid = validator.validate(XML_PATH, XSD_PATH);

        // Очікуємо true
        Assertions.assertTrue(isValid, "XML повинен проходити валідацію за XSD схемою");
    }

    @Test
    public void testValidateMissingFile() {
        // ! ВИПРАВЛЕННЯ: Створюємо об'єкт !
        XmlValidator validator = new XmlValidator();

        // Перевіряємо реакцію на файл, якого немає
        boolean isValid = validator.validate(WRONG_XML_PATH, XSD_PATH);

        // Очікуємо false
        Assertions.assertFalse(isValid, "Валідація не повинна проходити для відсутнього файлу");
    }
}