package packaging;

public class Package {
    private String packageType;
    private double weight;

    public Package(String packageType, double weight) {
        this.packageType = packageType;
        this.weight = weight;
    }

    public String getPackageType() {
        return packageType;
    }

    public double getWeight() {
        return weight;
    }

    @Override
    public String toString() {
        return "Package{packageType='" + packageType + "', weight=" + weight + "}";
    }
}
