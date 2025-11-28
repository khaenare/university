package tourist;

import java.util.List;

public class Main {

    public static void main(String[] args) {
        try {
            // Шлях до XML відносно кореня проєкту
            String xmlPath = "src/xml/tourist_vouchers.xml";

            TouristVouchersParser parser = new DomTouristVouchersParser();
            List<TouristVoucher> vouchers = parser.parse(xmlPath);

            // Простіше за все перевірити, що парсер реально щось повернув
            System.out.println("Кількість путівок: " + vouchers.size());
            for (TouristVoucher voucher : vouchers) {
                System.out.println(voucher);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
