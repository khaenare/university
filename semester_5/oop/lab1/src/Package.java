// Клас для упаковки кави
class Package {
    private String packageType; // тип упаковки (банка, пакетик и т.д.)
    private double weight; // вага упаковки в кг

    // Конструктор
    public Package(String packageType, double weight) {
        this.packageType = packageType;
        this.weight = weight;
    }

    // Геттеры и сеттеры
    public String getPackageType() {
        return packageType;
    }

    public void setPackageType(String packageType) {
        this.packageType = packageType;
    }

    public double getWeight() {
        return weight;
    }

    public void setWeight(double weight) {
        this.weight = weight;
    }

    @Override
    public String toString() {
        return "Package{packageType='" + packageType + "', weight=" + weight + "}";
    }
}

