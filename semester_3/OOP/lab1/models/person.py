class Person:
    """
    Базовый класс для представления человека.
    """

    def __init__(self, name: str, surname: str, email: str):
        self._name = name
        self._surname = surname
        self._email = email

    def get_full_name(self) -> str:
        """
        Возвращает полное имя человека.
        """
        return f"{self._name} {self._surname}"

    def get_email(self) -> str:
        """
        Возвращает электронную почту человека.
        """
        return self._email

    def set_email(self, email: str):
        """
        Устанавливает электронную почту человека.
        """
        self._email = email
