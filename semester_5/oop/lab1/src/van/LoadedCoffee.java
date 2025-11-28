package van;

import coffee.Coffee;
import packaging.PackageType;

// Клас для зберігання кави разом з упаковкою
public class LoadedCoffee {

    private Coffee coffee;        // Об'єкт кави
    private PackageType packType; // Тип упаковки

    public LoadedCoffee(Coffee coffee, PackageType packType) {
        this.coffee = coffee;
        this.packType = packType;
    }

    public Coffee getCoffee() {
        return coffee;
    }

    public PackageType getPackType() {
        return packType;
    }

    @Override
    public String toString() {
        return coffee.toString() + ", package=" + packType.name();
    }
}
