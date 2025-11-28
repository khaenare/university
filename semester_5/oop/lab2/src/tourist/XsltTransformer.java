package tourist;

import javax.xml.transform.Source;
import javax.xml.transform.Result;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.File;

/**
 * Клас для виконання XSLT-перетворень.
 */
public class XsltTransformer {

    /**
     * Виконати XSLT-перетворення XML-файлу.
     *
     * @param xmlPath    шлях до вхідного XML
     * @param xslPath    шлях до XSL-файлу
     * @param outputPath шлях до вихідного XML (куди зберегти результат)
     */
    public void transform(String xmlPath, String xslPath, String outputPath) {
        try {
            File xmlFile = new File(xmlPath);
            File xslFile = new File(xslPath);
            File outFile = new File(outputPath);

            if (!xmlFile.exists()) {
                System.out.println("XML-файл для XSLT не знайдено: " + xmlFile.getAbsolutePath());
                return;
            }
            if (!xslFile.exists()) {
                System.out.println("XSL-файл не знайдено: " + xslFile.getAbsolutePath());
                return;
            }

            // Джерела даних для трансформації
            Source xmlSource = new StreamSource(xmlFile);
            Source xslSource = new StreamSource(xslFile);
            Result result = new StreamResult(outFile);

            // Створення трансформера на базі XSL
            TransformerFactory factory = TransformerFactory.newInstance();
            Transformer transformer = factory.newTransformer(xslSource);

            // Виконання трансформації
            transformer.transform(xmlSource, result);

            System.out.println("XSLT-перетворення виконано успішно.");
            System.out.println("Результат збережено у файл: " + outFile.getAbsolutePath());
        } catch (Exception e) {
            // Спрощене логування помилки для лабораторної роботи
            System.out.println("Помилка під час XSLT-перетворення: " + e.getMessage());
        }
    }
}
