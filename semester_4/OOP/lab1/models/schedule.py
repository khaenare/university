from typing import List, Dict
from datetime import datetime, date

class Schedule:
    """
    Клас, що представляє розклад.
    """

    def __init__(self):
        self.events: List[Dict[str, object]] = []

    def add_event(self, event: Dict[str, object]):
        """
        Додає подію до розкладу.
        Очікується словник з ключами: 'title': str, 'date': date, 'time': str(optional)
        """
        if 'title' not in event or 'date' not in event:
            raise ValueError("Event must include at least 'title' and 'date'")
        if not isinstance(event['date'], date):
            raise TypeError("'date' must be a datetime.date instance")
        self.events.append(event)
        print(f"Event '{event['title']}' added to schedule.")

    def remove_event(self, event_title: str):
        """
        Видаляє подію з розкладу за назвою.
        """
        initial_count = len(self.events)
        self.events = [event for event in self.events if event.get('title') != event_title]
        if len(self.events) < initial_count:
            print(f"Event '{event_title}' removed from schedule.")
        else:
            print(f"No event found with title '{event_title}'.")

    def get_today_events(self) -> List[Dict[str, object]]:
        """
        Повертає список подій на сьогодні, відсортованих за часом (якщо задано).
        """
        today = datetime.now().date()
        today_events = [event for event in self.events if event.get('date') == today]
        return sorted(today_events, key=lambda e: e.get('time', '00:00'))
