package tourist;

import java.util.List;

public class Main {

    public static void main(String[] args) {
        try {
            String xmlPath = "src/xml/tourist_vouchers.xml";

            // DOM
            TouristVouchersParser domParser = new DomTouristVouchersParser();
            List<TouristVoucher> domVouchers = domParser.parse(xmlPath);
            System.out.println("DOM -> кількість путівок: " + domVouchers.size());

            // SAX
            TouristVouchersParser saxParser = new SaxTouristVouchersParser();
            List<TouristVoucher> saxVouchers = saxParser.parse(xmlPath);
            System.out.println("SAX -> кількість путівок: " + saxVouchers.size());

            // StAX
            TouristVouchersParser staxParser = new StaxTouristVouchersParser();
            List<TouristVoucher> staxVouchers = staxParser.parse(xmlPath);
            System.out.println("StAX -> кількість путівок: " + staxVouchers.size());

            for (TouristVoucher v : staxVouchers) {
                System.out.println("StAX: " + v);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
