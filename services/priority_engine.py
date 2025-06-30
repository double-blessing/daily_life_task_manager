from datetime import datetime

class PriorityEngine:
    def calculate_dynamic_priority(self, base_priority, due_date, time_estimate):
        """Calculate dynamic priority score (0-10) based on multiple factors"""
        now = datetime.now().date()
        days_remaining = (due_date - now).days

        # Time urgency factor (0-3)
        if days_remaining <= 0:
            time_urgency = 3
        elif days_remaining <= 1:
            time_urgency = 2.5
        elif days_remaining <= 3:
            time_urgency = 2
        elif days_remaining <= 7:
            time_urgency = 1.5
        else:
            time_urgency = 1

        # Time estimate factor (shorter tasks get slight boost)
        time_factor = 1 + (1 / (time_estimate / 5))

        # Calculate dynamic priority
        dynamic_priority = base_priority * time_urgency * time_factor

        # Normalize to 0-10 scale
        return min(10, dynamic_priority)