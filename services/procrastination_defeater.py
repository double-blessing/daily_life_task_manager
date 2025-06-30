import random
import streamlit as st  # Add this import at the top

class ProcrastinationDefeater:
    def generate_micro_steps(self, task):
        """Break task into tiny, manageable steps"""
        steps = []
        
        if "email" in task.title.lower():
            steps = [
                "Open email client",
                "Click 'Compose'",
                "Write subject line",
                "Write first sentence",
                "Complete email body",
                "Add recipients",
                "Hit send"
            ]
        elif "report" in task.title.lower():
            steps = [
                "Open document",
                "Write title",
                "Create outline",
                "Write first section",
                "Add data points",
                "Write conclusion",
                "Proofread"
            ]
        else:
            steps = [
                "Start task",
                "Do first part",
                "Continue working",
                "Overcome one obstacle",
                "Final push",
                "Complete task"
            ]
        
        # Random encouragement
        encouragements = [
            "You've got this!", 
            "Just start - the rest will follow!",
            "Small steps lead to big progress!",
            "Future you will thank present you!"
        ]
        
        steps.append(random.choice(encouragements))
        return steps
    
    def display_anti_procrastination_tools(self):
        st.subheader("🚀 Procrastination Combat Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 5-Minute Jumpstart")
            if st.button("Start 5-minute timer"):
                st.session_state.timer_started = True
                st.success("Timer started! Commit to just 5 minutes.")
            
            if st.button("Generate motivation quote"):
                quotes = [
                    "The best time to plant a tree was 20 years ago. The second best time is now.",
                    "Done is better than perfect.",
                    "You don't have to see the whole staircase, just take the first step.",
                    "Action is the foundational key to all success."
                ]
                st.info(random.choice(quotes))
        
        with col2:
            st.markdown("### Task Visualization")
            task_to_visualize = st.text_input("Imagine completing this task:")
            if task_to_visualize:
                st.markdown(f"Close your eyes and imagine how great it will feel to complete: **{task_to_visualize}**")
                st.markdown("Visualize the steps and the satisfaction of completion.")