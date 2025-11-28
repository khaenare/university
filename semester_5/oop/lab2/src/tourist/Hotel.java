package tourist;

/**
 * Модель готелю, що описує блок <hotel> у XML.
 */
public class Hotel {

    // Назва готелю
    private String name;

    // Кількість зірок (1-5)
    private int stars;

    // Тип номеру (SINGLE, DOUBLE, TRIPLE)
    private RoomType roomType;

    // Тип харчування (RO, BB, HB, FB, AI)
    private MealsType meals;

    // Наявність телевізора
    private boolean tv;

    // Наявність кондиціонера
    private boolean airConditioner;

    /**
     * Порожній конструктор потрібен для парсерів та можливих бібліотек.
     */
    public Hotel() {
    }

    /**
     * Повний конструктор для зручного створення об'єкту в коді.
     */
    public Hotel(String name,
                 int stars,
                 RoomType roomType,
                 MealsType meals,
                 boolean tv,
                 boolean airConditioner) {
        this.name = name;
        this.stars = stars;
        this.roomType = roomType;
        this.meals = meals;
        this.tv = tv;
        this.airConditioner = airConditioner;
    }

    // ===== Геттери та сеттери =====

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getStars() {
        return stars;
    }

    public void setStars(int stars) {
        this.stars = stars;
    }

    public RoomType getRoomType() {
        return roomType;
    }

    public void setRoomType(RoomType roomType) {
        this.roomType = roomType;
    }

    public MealsType getMeals() {
        return meals;
    }

    public void setMeals(MealsType meals) {
        this.meals = meals;
    }

    public boolean hasTv() {
        return tv;
    }

    public void setTv(boolean tv) {
        this.tv = tv;
    }

    public boolean hasAirConditioner() {
        return airConditioner;
    }

    public void setAirConditioner(boolean airConditioner) {
        this.airConditioner = airConditioner;
    }

    @Override
    public String toString() {
        // Коротке текстове представлення готелю для логування
        return "Hotel{" +
                "name='" + name + '\'' +
                ", stars=" + stars +
                ", roomType=" + roomType +
                ", meals=" + meals +
                ", tv=" + tv +
                ", airConditioner=" + airConditioner +
                '}';
    }
}
