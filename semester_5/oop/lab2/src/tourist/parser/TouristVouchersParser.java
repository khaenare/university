package tourist.parser;

import tourist.model.TouristVoucher;

import java.util.List;

/**
 * Спільний інтерфейс для всіх парсерів (DOM, SAX, StAX).
 * Дає змогу повертати колекцію TouristVoucher з XML-файлу.
 */
public interface TouristVouchersParser {

    /**
     * Розібрати XML-документ та створити колекцію туристичних путівок.
     *
     * @param xmlFilePath шлях до XML-файлу
     * @return список туристичних путівок
     * @throws Exception якщо сталася помилка під час розбору
     */
    List<TouristVoucher> parse(String xmlFilePath) throws Exception;
}
