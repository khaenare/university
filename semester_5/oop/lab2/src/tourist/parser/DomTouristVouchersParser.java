package tourist.parser;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import tourist.model.*;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Реалізація парсера на базі DOM.
 * Завантажує весь XML у пам'ять у вигляді дерева Document.
 */
public class DomTouristVouchersParser implements TouristVouchersParser {

    @Override
    public List<TouristVoucher> parse(String xmlFilePath) throws Exception {
        // Список, куди будемо складати всі знайдені путівки
        List<TouristVoucher> vouchers = new ArrayList<>();

        // Підготовка фабрики та будівника документів
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();

        // Завантажуємо та парсимо XML-файл
        Document document = builder.parse(new File(xmlFilePath));
        document.getDocumentElement().normalize();

        // Отримуємо всі вузли <tourist_voucher>
        NodeList voucherNodes = document.getElementsByTagName("tourist_voucher");

        for (int i = 0; i < voucherNodes.getLength(); i++) {
            Node node = voucherNodes.item(i);

            if (node.getNodeType() == Node.ELEMENT_NODE) {
                Element voucherElement = (Element) node;

                // Створюємо об'єкт TouristVoucher та заповнюємо поля
                TouristVoucher voucher = buildVoucherFromElement(voucherElement);

                vouchers.add(voucher);
            }
        }

        return vouchers;
    }

    /**
     * Створює об'єкт TouristVoucher з DOM-елемента <tourist_voucher>.
     */
    private TouristVoucher buildVoucherFromElement(Element voucherElement) {
        TouristVoucher voucher = new TouristVoucher();

        // ==== Атрибут id ====
        String id = voucherElement.getAttribute("id");
        voucher.setId(id);

        // ==== Прості текстові елементи ====
        String typeText = getChildTextContent(voucherElement, "type");
        String country = getChildTextContent(voucherElement, "country");
        String daysText = getChildTextContent(voucherElement, "days");
        String nightsText = getChildTextContent(voucherElement, "nights");
        String transportText = getChildTextContent(voucherElement, "transport");

        // Перетворення рядків у відповідні типи
        VoucherType type = VoucherType.valueOf(typeText);
        int days = Integer.parseInt(daysText);
        int nights = Integer.parseInt(nightsText);
        TransportType transport = TransportType.valueOf(transportText);

        voucher.setType(type);
        voucher.setCountry(country);
        voucher.setDays(days);
        voucher.setNights(nights);
        voucher.setTransport(transport);

        // ==== Вкладений елемент <hotel> ====
        Element hotelElement = (Element) voucherElement.getElementsByTagName("hotel").item(0);
        Hotel hotel = buildHotelFromElement(hotelElement);
        voucher.setHotel(hotel);

        // ==== Елемент <cost> з атрибутом currency ====
        Element costElement = (Element) voucherElement.getElementsByTagName("cost").item(0);
        String costText = costElement.getTextContent().trim();
        String currency = costElement.getAttribute("currency");

        BigDecimal cost = new BigDecimal(costText);
        voucher.setCost(cost);
        voucher.setCurrency(currency);

        return voucher;
    }

    /**
     * Створює об'єкт Hotel з DOM-елемента <hotel>.
     */
    private Hotel buildHotelFromElement(Element hotelElement) {
        Hotel hotel = new Hotel();

        String name = getChildTextContent(hotelElement, "name");
        String starsText = getChildTextContent(hotelElement, "stars");
        String roomTypeText = getChildTextContent(hotelElement, "room_type");
        String mealsText = getChildTextContent(hotelElement, "meals");
        String tvText = getChildTextContent(hotelElement, "tv");
        String acText = getChildTextContent(hotelElement, "air_conditioner");

        int stars = Integer.parseInt(starsText);
        RoomType roomType = RoomType.valueOf(roomTypeText);
        MealsType meals = MealsType.valueOf(mealsText);
        boolean tv = Boolean.parseBoolean(tvText);
        boolean airConditioner = Boolean.parseBoolean(acText);

        hotel.setName(name);
        hotel.setStars(stars);
        hotel.setRoomType(roomType);
        hotel.setMeals(meals);
        hotel.setTv(tv);
        hotel.setAirConditioner(airConditioner);

        return hotel;
    }

    /**
     * Допоміжний метод: повертає текст елемента-дитини за його ім'ям.
     *
     * @param parent  батьківський елемент
     * @param tagName ім'я дочірнього елемента
     * @return текстовий вміст дочірнього елемента або порожній рядок
     */
    private String getChildTextContent(Element parent, String tagName) {
        NodeList nodes = parent.getElementsByTagName(tagName);
        if (nodes.getLength() == 0) {
            return "";
        }
        return nodes.item(0).getTextContent().trim();
    }
}
