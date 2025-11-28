package tourist.util;

import org.xml.sax.SAXException;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.File;
import java.io.IOException;

/**
 * Клас для валідації XML-документів за схемою XSD.
 */
public class XmlValidator {

    /**
     * Перевірити, чи відповідає XML-файл заданій XSD-схемі.
     *
     * @param xmlPath шлях до XML-файлу
     * @param xsdPath шлях до XSD-схеми
     * @return true, якщо XML валідний, інакше false
     */
    public boolean validate(String xmlPath, String xsdPath) {
        File xmlFile = new File(xmlPath);
        File xsdFile = new File(xsdPath);

        // Перевіряємо, що файли взагалі існують
        if (!xmlFile.exists()) {
            System.out.println("XML-файл не знайдено: " + xmlFile.getAbsolutePath());
            return false;
        }
        if (!xsdFile.exists()) {
            System.out.println("XSD-файл не знайдено: " + xsdFile.getAbsolutePath());
            return false;
        }

        try {
            // Фабрика схем для W3C XML Schema (XSD)
            SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);

            // Створюємо об'єкт Schema на основі XSD-файлу
            Schema schema = factory.newSchema(xsdFile);

            // Валідатор для перевірки конкретного XML
            Validator validator = schema.newValidator();

            // Виконуємо перевірку
            validator.validate(new StreamSource(xmlFile));

            // Якщо сюди дійшли без виключення — XML валідний
            System.out.println("XML валідний відносно схеми XSD.");
            return true;
        } catch (SAXException e) {
            // Помилка структури / невідповідність схемі
            System.out.println("Помилка валідації XML: " + e.getMessage());
        } catch (IOException e) {
            // Проблеми з читанням файлів
            System.out.println("Помилка читання файлів під час валідації: " + e.getMessage());
        }

        return false;
    }
}
