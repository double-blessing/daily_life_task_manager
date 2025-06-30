class ContextAnalyzer:
    def rank_tasks(self, tasks, current_energy, available_time, location):
        """Sort tasks based on current context"""
        ranked = []

        for task in tasks:
            if task.completed:
                continue

            # Ensure energy_level and time_estimate are not None or zero to avoid errors
            task_energy = task.energy_level if task.energy_level else 5
            task_time = task.time_estimate if task.time_estimate else 30

            energy_match = 10 - abs(current_energy - task_energy)
            time_suitability = min(1, available_time / task_time) * 10

            if location == "Office" and "meeting" in task.title.lower():
                location_boost = 3
            elif location == "Home" and "call" not in task.title.lower():
                location_boost = 2
            else:
                location_boost = 1

            suitability_score = (
                (task.dynamic_priority * 4) +
                (energy_match * 3) +
                (time_suitability * 2) +
                location_boost
            )

            ranked.append((suitability_score, task))

        # Sort by highest suitability first
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [task for (score, task) in ranked]
