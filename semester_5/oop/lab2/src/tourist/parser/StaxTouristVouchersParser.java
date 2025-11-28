package tourist.parser;

import tourist.model.*;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Реалізація парсера на базі StAX (pull-парсер).
 * Ми самі "тягнемо" події з XMLStreamReader та будуємо об'єкти.
 */
public class StaxTouristVouchersParser implements TouristVouchersParser {

    @Override
    public List<TouristVoucher> parse(String xmlFilePath) throws Exception {
        List<TouristVoucher> vouchers = new ArrayList<>();

        // Поточні об'єкти під час розбору
        TouristVoucher currentVoucher = null;
        Hotel currentHotel = null;
        String currentCurrency = null;

        // Поточна назва елемента, щоб коректно обробляти текст
        String currentElementName = null;

        XMLInputFactory factory = XMLInputFactory.newInstance();

        // Використовуємо try-with-resources, щоб коректно закрити потік
        try (InputStream is = new FileInputStream(xmlFilePath)) {
            XMLStreamReader reader = factory.createXMLStreamReader(is);

            while (reader.hasNext()) {
                int eventType = reader.next();

                switch (eventType) {
                    case XMLStreamConstants.START_ELEMENT:
                        currentElementName = reader.getLocalName();

                        if ("tourist_voucher".equals(currentElementName)) {
                            // Початок нової путівки
                            currentVoucher = new TouristVoucher();

                            // Зчитуємо атрибут id
                            String id = reader.getAttributeValue(null, "id");
                            currentVoucher.setId(id);
                        } else if ("hotel".equals(currentElementName)) {
                            // Початок блоку готелю
                            currentHotel = new Hotel();
                        } else if ("cost".equals(currentElementName)) {
                            // Атрибут currency в <cost>
                            currentCurrency = reader.getAttributeValue(null, "currency");
                        }
                        break;

                    case XMLStreamConstants.CHARACTERS:
                        // Текст може приходити кількома подіями, тому беремо trim і перевіряємо, що не порожньо
                        String text = reader.getText().trim();
                        if (text.isEmpty() || currentElementName == null) {
                            break;
                        }

                        // Далі діємо в залежності від поточного елемента
                        switch (currentElementName) {
                            // ===== Поля путівки =====
                            case "type":
                                if (currentVoucher != null) {
                                    currentVoucher.setType(VoucherType.valueOf(text));
                                }
                                break;

                            case "country":
                                if (currentVoucher != null) {
                                    currentVoucher.setCountry(text);
                                }
                                break;

                            case "days":
                                if (currentVoucher != null) {
                                    currentVoucher.setDays(Integer.parseInt(text));
                                }
                                break;

                            case "nights":
                                if (currentVoucher != null) {
                                    currentVoucher.setNights(Integer.parseInt(text));
                                }
                                break;

                            case "transport":
                                if (currentVoucher != null) {
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
                                if (currentHotel != null) {
                                    currentHotel.setStars(Integer.parseInt(text));
                                }
                                break;

                            case "room_type":
                                if (currentHotel != null) {
                                    currentHotel.setRoomType(RoomType.valueOf(text));
                                }
                                break;

                            case "meals":
                                if (currentHotel != null) {
                                    currentHotel.setMeals(MealsType.valueOf(text));
                                }
                                break;

                            case "tv":
                                if (currentHotel != null) {
                                    currentHotel.setTv(Boolean.parseBoolean(text));
                                }
                                break;

                            case "air_conditioner":
                                if (currentHotel != null) {
                                    currentHotel.setAirConditioner(Boolean.parseBoolean(text));
                                }
                                break;

                            // ===== Вартість =====
                            case "cost":
                                if (currentVoucher != null) {
                                    BigDecimal cost = new BigDecimal(text);
                                    currentVoucher.setCost(cost);
                                    currentVoucher.setCurrency(currentCurrency);
                                }
                                break;

                            default:
                                // Інші елементи нас не цікавлять
                                break;
                        }
                        break;

                    case XMLStreamConstants.END_ELEMENT:
                        String endName = reader.getLocalName();

                        if ("hotel".equals(endName)) {
                            // Коли завершується <hotel>, прив'язуємо його до поточної путівки
                            if (currentVoucher != null) {
                                currentVoucher.setHotel(currentHotel);
                            }
                            currentHotel = null;
                        } else if ("tourist_voucher".equals(endName)) {
                            // Кінець однієї путівки — додаємо до списку
                            if (currentVoucher != null) {
                                vouchers.add(currentVoucher);
                            }
                            currentVoucher = null;
                        }

                        // Скидаємо назву елемента, щоб уникнути помилкового використання
                        currentElementName = null;
                        break;

                    default:
                        // Інші типи подій нам не потрібні
                        break;
                }
            }

            reader.close();
        }

        return vouchers;
    }
}
