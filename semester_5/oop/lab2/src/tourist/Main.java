package tourist;

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
}
