class Person:
    """
    Базовий клас для представлення людини.
    """

    def __init__(self, name: str, surname: str, email: str):
        self.name = name
        self.surname = surname
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty.")
        self._name = value

    @property
    def surname(self) -> str:
        return self._surname

    @surname.setter
    def surname(self, value: str):
        if not value:
            raise ValueError("Surname cannot be empty.")
        self._surname = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email address.")
        self._email = value

    def get_full_name(self) -> str:
        """
        Повертає повне ім'я людини.
        """
        return f"{self.name} {self.surname}"

    def get_email(self) -> str:
        """
        Повертає електронну пошту людини.
        """
        return self.email

    def set_email(self, email: str):
        """
        Встановлює електронну пошту людини.
        """
        self.email = email

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"
