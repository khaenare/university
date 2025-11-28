package tourist;

import java.util.Comparator;

/**
 * Компаратор для сортування туристичних путівок
 * за кількістю днів (поле days).
 */
public class TouristVoucherDaysComparator implements Comparator<TouristVoucher> {

    @Override
    public int compare(TouristVoucher o1, TouristVoucher o2) {
        if (o1 == null && o2 == null) {
            return 0;
        }
        if (o1 == null) {
            return -1;
        }
        if (o2 == null) {
            return 1;
        }

        // Основне порівняння за кількістю днів
        int result = Integer.compare(o1.getDays(), o2.getDays());

        // Якщо днів однаково, порівнюємо за вартістю
        if (result == 0) {
            if (o1.getCost() == null && o2.getCost() == null) {
                return 0;
            }
            if (o1.getCost() == null) {
                return -1;
            }
            if (o2.getCost() == null) {
                return 1;
            }
            return o1.getCost().compareTo(o2.getCost());
        }

        return result;
    }
}
