package tourist;

import java.util.Collections;
import java.util.List;

/**
 * Невелика точка входу для демонстрації роботи парсерів і сортування.
 */
public class Main {

    public static void main(String[] args) {
        try {
            String xmlPath = "src/xml/tourist_vouchers.xml";

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

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
