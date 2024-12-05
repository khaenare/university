from typing import List

class Schedule:
    """
    Клас, що представляє розклад.
    """

    def __init__(self):
        self.events: List[dict] = []

    def add_event(self, event: dict):
        """
        Додає подію до розкладу.
        """
        self.events.append(event)
        print(f"Event '{event.get('title')}' added to schedule.")

    def remove_event(self, event_title: str):
        """
        Видаляє подію з розкладу за назвою.
        """
        self.events = [event for event in self.events if event.get('title') != event_title]
        print(f"Event '{event_title}' removed from schedule.")

    def get_today_events(self) -> List[dict]:
        """
        Повертає список подій на сьогодні.
        """
        from datetime import datetime
        today = datetime.now().date()
        today_events = [event for event in self.events if event.get('date') == today]
        return today_events
