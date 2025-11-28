# Лабораторна робота №2 з ООП  
**Тема:** Обробка XML-документів у мові Java (DOM, SAX, StAX, XSD, XSLT)

---

## 1. Мета роботи

Ознайомитися з основними підходами до обробки XML-документів у Java,  
навчитися:

- описувати структуру XML за допомогою XSD-схеми;
- валідовувати XML-документи за XSD;
- розбирати XML різними парсерами (DOM, SAX, StAX);
- будувати об’єктну модель предметної області;
- виконувати сортування об’єктів за допомогою `Comparator`;
- застосовувати XSLT для перетворення та групування даних.

---

## 2. Предметна область

Предметна область – **туристичні путівки** (Tourist voucher).

Кожна путівка описується:

- тип путівки: `WEEKEND`, `EXCURSION`, `REST`, `PILGRIMAGE`;
- країна подорожі;
- кількість днів та ночей;
- вид транспорту: `AIR`, `TRAIN`, `BUS`, `SHIP`;
- характеристика готелю:
  - назва;
  - кількість зірок (1–5);
  - тип номеру: `SINGLE`, `DOUBLE`, `TRIPLE`;
  - тип харчування: `RO`, `BB`, `HB`, `FB`, `AI`;
  - наявність телевізора та кондиціонера;
- вартість путівки з атрибутом валюти (`EUR`, `USD`, `UAH`).

---

## 3. Структура проєкту

### 3.1. Дерево файлів

```text
lab2/
  src/
    tourist/
      comparator/
        TouristVoucherCostComparator.java
        TouristVoucherDaysComparator.java

      model/
        Hotel.java
        MealsType.java
        RoomType.java
        TouristVoucher.java
        TransportType.java
        VoucherType.java

      parser/
        DomTouristVouchersParser.java
        SaxTouristVouchersParser.java
        StaxTouristVouchersParser.java
        TouristVouchersParser.java

      util/
        XmlValidator.java
        Main.java

    xml/
      tourist_vouchers.xml
      tourist_vouchers.xsd
      tourist_vouchers_grouped.xml

    xsl/
      tourist_vouchers_group_by_type.xsl
```
Основний пакет програми – `tourist`.
Підпакети:

```text
tourist.model
tourist.parser
tourist.comparator
tourist.util
```

---

## 4. XML-документ та XSD-схема

### 4.1. XML-документ

Файл: `src/xml/tourist_vouchers.xml`

Містить колекцію елементів:

* кореневий елемент: `<tourist_vouchers>`;
* вкладені елементи: `<tourist_voucher id="...">` з повним набором полів;
* елемент `<cost>` має атрибут `currency`.

### 4.2. XSD-схема

Файл: `src/xml/tourist_vouchers.xsd`

Схема описує:

* прості типи з обмеженнями та переліками:

    * `VoucherType`, `TransportType`, `RoomType`, `MealsType`;
    * кількість днів/ночей (`DaysType`), зірок готелю (`StarsType`), вартість (`CostType`), валюту (`CurrencyType`);
* комплексні типи:

    * `HotelType` – структура елементу `<hotel>`;
    * `TouristVoucherType` – структура `<tourist_voucher>` з атрибутом `id` типу `xs:ID`;
    * `TouristVouchersType` – колекція всіх путівок;
* кореневий елемент `<tourist_vouchers>` на базі `TouristVouchersType`.

---

## 5. Об’єктна модель у Java

### 5.1. Перелічувані типи (пакет `tourist.model`)

* `VoucherType` – тип путівки (`WEEKEND`, `EXCURSION`, `REST`, `PILGRIMAGE`).
* `TransportType` – вид транспорту (`AIR`, `TRAIN`, `BUS`, `SHIP`).
* `RoomType` – тип номеру (`SINGLE`, `DOUBLE`, `TRIPLE`).
* `MealsType` – тип харчування (`RO`, `BB`, `HB`, `FB`, `AI`).

### 5.2. Клас `Hotel`

Файл: `tourist/model/Hotel.java`
Описує готель: назва, зірки, тип номеру, тип харчування, наявність TV та кондиціонера.
Містить:

* приватні поля;
* конструктори (порожній та повний);
* геттери/сеттери;
* метод `toString()` для зручного виводу.

### 5.3. Клас `TouristVoucher`

Файл: `tourist/model/TouristVoucher.java`
Описує одну туристичну путівку:

* атрибут `id`;
* поля `type`, `country`, `days`, `nights`, `transport`;
* поле `hotel` типу `Hotel`;
* поле `cost` типу `BigDecimal` та рядкове поле `currency`;
* геттери/сеттери, конструктор, `toString()`.

---

## 6. Реалізація парсерів (пакет `tourist.parser`)

Інтерфейс:

```java
public interface TouristVouchersParser {
    List<TouristVoucher> parse(String xmlFilePath) throws Exception;
}
```

### 6.1. DOM-парсер

Файл: `tourist/parser/DomTouristVouchersParser.java`

* використовує `DocumentBuilderFactory` та `DocumentBuilder`;
* завантажує XML у дерево `Document`;
* проходить по елементах `<tourist_voucher>` і створює об’єкти `TouristVoucher` та `Hotel`.

### 6.2. SAX-парсер

Файл: `tourist/parser/SaxTouristVouchersParser.java`

* наслідує `DefaultHandler`;
* обробляє події `startElement`, `endElement`, `characters`;
* поступово будує `TouristVoucher` і `Hotel` під час проходу по XML.

### 6.3. StAX-парсер

Файл: `tourist/parser/StaxTouristVouchersParser.java`

* використовує `XMLStreamReader`;
* реалізує pull-підхід через події `START_ELEMENT`, `CHARACTERS`, `END_ELEMENT`.

---

## 7. Сортування путівок (пакет `tourist.comparator`)

### 7.1. Сортування за вартістю

Файл: `tourist/comparator/TouristVoucherCostComparator.java`

Порівнює путівки за полем `cost` (за зростанням).
При однаковій вартості додатково порівнює кількість днів (`days`).

### 7.2. Сортування за кількістю днів

Файл: `tourist/comparator/TouristVoucherDaysComparator.java`

Порівнює путівки за полем `days`.
При однаковій кількості днів порівнює за вартістю.

Сортування демонструється у `Main.java` за допомогою `Collections.sort(...)`.

---

## 8. Валідація XML за XSD (пакет `tourist.util`)

Файл: `tourist/util/XmlValidator.java`

* використовує `SchemaFactory`, `Schema`, `Validator`;
* метод `validate(String xmlPath, String xsdPath)`:

    * повертає `true`, якщо XML відповідає схемі;
    * виводить повідомлення про помилки валідації у консоль.

---

## 9. XSLT-перетворення та групування

### 9.1. XSLT-файл

Файл: `src/xsl/tourist_vouchers_group_by_type.xsl`

* групує всі елементи `<tourist_voucher>` за значенням елемента `<type>`;
* формує нову структуру:

```xml
<tourist_vouchers_grouped>
    <WEEKEND>...</WEEKEND>
    <EXCURSION>...</EXCURSION>
    <REST>...</REST>
    <PILGRIMAGE>...</PILGRIMAGE>
</tourist_vouchers_grouped>
```

Результат трансформації зберігається у `src/xml/tourist_vouchers_grouped.xml`.

---

## 10. Демонстраційний запуск програми

Файл: `tourist/util/Main.java`

Основні кроки у методі `main`:

1. валідація XML-документа `tourist_vouchers.xml` за XSD `tourist_vouchers.xsd`;
2. парсинг XML трьома парсерами: DOM, SAX, StAX;
3. виведення кількості об’єктів, отриманих кожним парсером;
4. сортування колекції путівок:

    * за вартістю;
    * за кількістю днів;
5. запуск XSLT-перетворення для групування путівок за типом
   (результат у `tourist_vouchers_grouped.xml`).

Для запуску достатньо виконати метод `main` у класі `tourist.util.Main`.
