package tourist;

import java.math.BigDecimal;

/**
 * Модель однієї туристичної путівки.
 * Відповідає елементу <tourist_voucher> у XML-документі.
 */
public class TouristVoucher {

    // ===== Основні поля, що напряму відповідають XML =====

    // XML-атрибут id (тип xs:ID у схемі XSD)
    private String id;

    // Тип путівки: WEEKEND, EXCURSION, REST, PILGRIMAGE
    private VoucherType type;

    // Країна подорожі (Country)
    private String country;

    // Кількість днів (Number days)
    private int days;

    // Кількість ночей (Number nights)
    private int nights;

    // Транспорт: AIR, TRAIN, BUS, SHIP
    private TransportType transport;

    // Характеристики готелю (вкладений елемент <hotel>)
    private Hotel hotel;

    // Вартість путівки
    private BigDecimal cost;

    // Валюта вартості (атрибут currency у елементі <cost>)
    private String currency;

    /**
     * Порожній конструктор потрібен для створення об'єкту парсерами.
     */
    public TouristVoucher() {
    }

    /**
     * Повний конструктор для зручного створення об'єкту в коді.
     */
    public TouristVoucher(String id,
                          VoucherType type,
                          String country,
                          int days,
                          int nights,
                          TransportType transport,
                          Hotel hotel,
                          BigDecimal cost,
                          String currency) {
        this.id = id;
        this.type = type;
        this.country = country;
        this.days = days;
        this.nights = nights;
        this.transport = transport;
        this.hotel = hotel;
        this.cost = cost;
        this.currency = currency;
    }

    // ===== Геттери та сеттери =====

    public String getId() {
        return id;
    }

    public void setId(String id) {
        // Тут ми можемо додатково перевіряти формат ID за потреби
        this.id = id;
    }

    public VoucherType getType() {
        return type;
    }

    public void setType(VoucherType type) {
        this.type = type;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public int getDays() {
        return days;
    }

    public void setDays(int days) {
        this.days = days;
    }

    public int getNights() {
        return nights;
    }

    public void setNights(int nights) {
        this.nights = nights;
    }

    public TransportType getTransport() {
        return transport;
    }

    public void setTransport(TransportType transport) {
        this.transport = transport;
    }

    public Hotel getHotel() {
        return hotel;
    }

    public void setHotel(Hotel hotel) {
        this.hotel = hotel;
    }

    public BigDecimal getCost() {
        return cost;
    }

    public void setCost(BigDecimal cost) {
        this.cost = cost;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        // У схемі XSD валюта обмежена значеннями EUR, USD, UAH
        this.currency = currency;
    }

    @Override
    public String toString() {
        // Короткий опис путівки для логування / відладочного виводу
        return "TouristVoucher{" +
                "id='" + id + '\'' +
                ", type=" + type +
                ", country='" + country + '\'' +
                ", days=" + days +
                ", nights=" + nights +
                ", transport=" + transport +
                ", hotel=" + hotel +
                ", cost=" + cost +
                ' ' + currency +
                '}';
    }
}
