class Person:
    """
    Базовий клас для представлення людини.
    """

    def __init__(self, name: str, surname: str, email: str):
        self._name = name
        self._surname = surname
        self._email = email

    def get_full_name(self) -> str:
        """
        Повертає повне ім'я людини.
        """
        return f"{self._name} {self._surname}"

    def get_email(self) -> str:
        """
        Повертає електронну пошту людини.
        """
        return self._email

    def set_email(self, email: str):
        """
        Встановлює електронну пошту людини.
        """
        self._email = email
