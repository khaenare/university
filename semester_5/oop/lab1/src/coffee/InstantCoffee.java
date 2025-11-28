package coffee;

// Підклас для розчинної кави
public class InstantCoffee extends Coffee {
    private String form; // Наприклад "банка" або "пакетик"

    public InstantCoffee(String name, double price, double volume) {
        super(name, price, volume);
        this.form = "Can"; // Значення за замовчуванням
    }

    @Override
    public String toString() {
        return super.toString() + ", form='" + form + "'";
    }
}

