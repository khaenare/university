package tourist;

import tourist.comparator.TouristVoucherCostComparator;
import tourist.comparator.TouristVoucherDaysComparator;
import tourist.model.TouristVoucher;
import tourist.parser.DomTouristVouchersParser;
import tourist.parser.SaxTouristVouchersParser;
import tourist.parser.StaxTouristVouchersParser;
import tourist.parser.TouristVouchersParser;
import tourist.util.XmlValidator;

import javax.xml.transform.Result;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.File;
import java.util.Collections;
import java.util.List;

/**
 * Невелика точка входу для демонстрації роботи:
 * - валідація XML за XSD;
 * - парсери DOM, SAX, StAX;
 * - сортування;
 * - XSLT-перетворення.
 */
public class Main {

    public static void main(String[] args) {
        try {
            String xmlPath = "src/xml/tourist_vouchers.xml";
            String xsdPath = "src/xml/tourist_vouchers.xsd";
            String xslPath = "src/xsl/tourist_vouchers_group_by_type.xsl";
            String groupedOutputPath = "src/xml/tourist_vouchers_grouped.xml";

            // ==== Валідація XML за XSD ====
            XmlValidator validator = new XmlValidator();
            boolean isValid = validator.validate(xmlPath, xsdPath);
            System.out.println("Результат валідації: " + isValid);
            System.out.println();

            // ==== Парсинг DOM ====
            TouristVouchersParser domParser = new DomTouristVouchersParser();
            List<TouristVoucher> domVouchers = domParser.parse(xmlPath);
            System.out.println("DOM -> кількість путівок: " + domVouchers.size());

            // ==== Парсинг SAX ====
            TouristVouchersParser saxParser = new SaxTouristVouchersParser();
            List<TouristVoucher> saxVouchers = saxParser.parse(xmlPath);
            System.out.println("SAX -> кількість путівок: " + saxVouchers.size());

            // ==== Парсинг StAX ====
            TouristVouchersParser staxParser = new StaxTouristVouchersParser();
            List<TouristVoucher> staxVouchers = staxParser.parse(xmlPath);
            System.out.println("StAX -> кількість путівок: " + staxVouchers.size());

            // ==== Сортування за вартістю ====
            System.out.println("\nСортування за вартістю (за зростанням):");
            Collections.sort(staxVouchers, new TouristVoucherCostComparator());
            for (TouristVoucher voucher : staxVouchers) {
                System.out.println(voucher);
            }

            // ==== Сортування за кількістю днів ====
            System.out.println("\nСортування за кількістю днів (за зростанням):");
            Collections.sort(staxVouchers, new TouristVoucherDaysComparator());
            for (TouristVoucher voucher : staxVouchers) {
                System.out.println(voucher);
            }

            // ==== XSLT-перетворення (групування за type) ====
            System.out.println("\nЗапуск XSLT-перетворення (групування путівок за типом)...");
            XsltTransformer xsltTransformer = new XsltTransformer();
            xsltTransformer.transform(xmlPath, xslPath, groupedOutputPath);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Клас для виконання XSLT-перетворень.
     */
    public static class XsltTransformer {

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
}
