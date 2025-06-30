from datetime import datetime

class PriorityEngine:
    def calculate_dynamic_priority(self, base_priority, due_date, time_estimate):
        """Calculate dynamic priority score (0-10) based on multiple factors"""
        # Ensure due_date is a datetime object
        if not isinstance(due_date, datetime):
            # Handle case where due_date might be a date object or None
            if due_date:
                due_date = datetime.combine(due_date, datetime.min.time())
            else:
                # If no due date, urgency is low
                return base_priority 

        now = datetime.now()
        
        # Time urgency factor (0-3)
        if due_date <= now:
            time_urgency = 3
        else:
            days_remaining = (due_date - now).days
            if days_remaining <= 1:
                time_urgency = 2.5
            elif days_remaining <= 3:
                time_urgency = 2
            elif days_remaining <= 7:
                time_urgency = 1.5
            else:
                time_urgency = 1

        # Time estimate factor (shorter tasks get slight boost)
        time_factor = 1 + (1 / (time_estimate / 5)) if time_estimate > 0 else 1

        # Calculate dynamic priority
        dynamic_priority = base_priority * time_urgency * time_factor

        # Normalize to 0-10 scale
        return min(10, max(0, dynamic_priority))
