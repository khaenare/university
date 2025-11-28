package tourist.comparator;

import tourist.model.TouristVoucher;

import java.util.Comparator;

/**
 * Компаратор для сортування туристичних путівок за вартістю.
 * Сортування виконується за зростанням значення cost.
 */
public class TouristVoucherCostComparator implements Comparator<TouristVoucher> {

    @Override
    public int compare(TouristVoucher o1, TouristVoucher o2) {
        // Перевірка на null для безпечного порівняння
        if (o1 == null && o2 == null) {
            return 0;
        }
        if (o1 == null) {
            return -1;
        }
        if (o2 == null) {
            return 1;
        }

        // Якщо cost відсутній, вважаємо, що така путівка "дешевша"
        if (o1.getCost() == null && o2.getCost() == null) {
            return 0;
        }
        if (o1.getCost() == null) {
            return -1;
        }
        if (o2.getCost() == null) {
            return 1;
        }

        // Основне порівняння за вартістю
        int result = o1.getCost().compareTo(o2.getCost());

        // Якщо вартість однакова, додатково порівнюємо за кількістю днів
        if (result == 0) {
            return Integer.compare(o1.getDays(), o2.getDays());
        }

        return result;
    }
}
