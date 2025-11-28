package tourist;

import org.xml.sax.Attributes;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.File;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Реалізація парсера на базі SAX.
 * SAX читає XML потоком та викликає колбеки startElement/endElement/characters.
 */
public class SaxTouristVouchersParser extends DefaultHandler implements TouristVouchersParser {

    // Колекція всіх знайдених путівок
    private List<TouristVoucher> vouchers;

    // Поточна путівка, яку зараз будуємо
    private TouristVoucher currentVoucher;

    // Поточний готель
    private Hotel currentHotel;

    // Поточний текстовий вміст між тегами
    private StringBuilder content;

    // Тимчасове зберігання валюти для <cost>
    private String currentCurrency;

    @Override
    public List<TouristVoucher> parse(String xmlFilePath) throws Exception {
        // ініціалізуємо колекцію перед кожним парсингом
        vouchers = new ArrayList<>();

        SAXParserFactory factory = SAXParserFactory.newInstance();
        SAXParser parser = factory.newSAXParser();

        // Запускаємо парсинг; this – це і є обробник подій
        parser.parse(new File(xmlFilePath), this);

        return vouchers;
    }

    @Override
    public void startElement(String uri,
                             String localName,
                             String qName,
                             Attributes attributes) {
        // Кожен раз, коли починається елемент, готуємо новий буфер для тексту
        content = new StringBuilder();

        if ("tourist_voucher".equals(qName)) {
            // Старт нового об'єкта путівки
            currentVoucher = new TouristVoucher();

            // Читаємо атрибут id
            String id = attributes.getValue("id");
            currentVoucher.setId(id);
        } else if ("hotel".equals(qName)) {
            // Старт блоку готелю
            currentHotel = new Hotel();
        } else if ("cost".equals(qName)) {
            // Пам'ятаємо валюту, щоб використати її в endElement
            currentCurrency = attributes.getValue("currency");
        }
    }

    @Override
    public void characters(char[] ch, int start, int length) {
        // Накопичуємо текст між тегами (може приходити шматками)
        if (content != null) {
            content.append(ch, start, length);
        }
    }

    @Override
    public void endElement(String uri,
                           String localName,
                           String qName) {

        String text = content != null ? content.toString().trim() : "";

        switch (qName) {
            // ===== Поля туристичної путівки =====
            case "type":
                if (currentVoucher != null && !text.isEmpty()) {
                    currentVoucher.setType(VoucherType.valueOf(text));
                }
                break;

            case "country":
                if (currentVoucher != null) {
                    currentVoucher.setCountry(text);
                }
                break;

            case "days":
                if (currentVoucher != null && !text.isEmpty()) {
                    currentVoucher.setDays(Integer.parseInt(text));
                }
                break;

            case "nights":
                if (currentVoucher != null && !text.isEmpty()) {
                    currentVoucher.setNights(Integer.parseInt(text));
                }
                break;

            case "transport":
                if (currentVoucher != null && !text.isEmpty()) {
                    currentVoucher.setTransport(TransportType.valueOf(text));
                }
                break;

            // ===== Поля готелю =====
            case "name":
                if (currentHotel != null) {
                    currentHotel.setName(text);
                }
                break;

            case "stars":
                if (currentHotel != null && !text.isEmpty()) {
                    currentHotel.setStars(Integer.parseInt(text));
                }
                break;

            case "room_type":
                if (currentHotel != null && !text.isEmpty()) {
                    currentHotel.setRoomType(RoomType.valueOf(text));
                }
                break;

            case "meals":
                if (currentHotel != null && !text.isEmpty()) {
                    currentHotel.setMeals(MealsType.valueOf(text));
                }
                break;

            case "tv":
                if (currentHotel != null && !text.isEmpty()) {
                    currentHotel.setTv(Boolean.parseBoolean(text));
                }
                break;

            case "air_conditioner":
                if (currentHotel != null && !text.isEmpty()) {
                    currentHotel.setAirConditioner(Boolean.parseBoolean(text));
                }
                break;

            case "hotel":
                // Коли закінчився блок <hotel>, прикріплюємо його до поточної путівки
                if (currentVoucher != null) {
                    currentVoucher.setHotel(currentHotel);
                }
                break;

            // ===== Вартість путівки =====
            case "cost":
                if (currentVoucher != null && !text.isEmpty()) {
                    BigDecimal cost = new BigDecimal(text);
                    currentVoucher.setCost(cost);
                    currentVoucher.setCurrency(currentCurrency);
                }
                break;

            // ===== Завершення всієї путівки =====
            case "tourist_voucher":
                // Додаємо побудовану путівку до колекції
                if (currentVoucher != null) {
                    vouchers.add(currentVoucher);
                }
                // Скидаємо посилання, щоб уникнути помилок
                currentVoucher = null;
                currentHotel = null;
                currentCurrency = null;
                break;

            default:
                // Для інших тегів нічого не робимо
                break;
        }
    }
}
