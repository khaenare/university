from typing import List

class Schedule:
    """
    Класс, представляющий расписание.
    """

    def __init__(self):
        self.events: List[dict] = []

    def add_event(self, event: dict):
        """
        Добавляет событие в расписание.
        """
        self.events.append(event)
        print(f"Событие '{event.get('title')}' добавлено в расписание.")

    def remove_event(self, event_title: str):
        """
        Удаляет событие из расписания по названию.
        """
        self.events = [event for event in self.events if event.get('title') != event_title]
        print(f"Событие '{event_title}' удалено из расписания.")

    def get_today_events(self) -> List[dict]:
        """
        Возвращает список событий на сегодня.
        """
        from datetime import datetime
        today = datetime.now().date()
        today_events = [event for event in self.events if event.get('date') == today]
        return today_events
