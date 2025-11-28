package packaging;

// Типи упаковки з фіксованим об'ємом
public enum PackageType {

    DENSE(0.30),   // щільна упаковка
    LIGHT(0.10);   // нещільна упаковка

    private final double volume;

    PackageType(double volume) {
        this.volume = volume;
    }

    public double getVolume() {
        return volume;
    }
}
