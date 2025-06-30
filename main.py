import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
import plotly.express as px

# Corrected imports from your new package
from services.task import Task
from services.priority_engine import PriorityEngine
from services.context_analyzer import ContextAnalyzer
from services.procrastination_defeater import ProcrastinationDefeater

# Initialize components
priority_engine = PriorityEngine()
context_analyzer = ContextAnalyzer()
procrastination_defeater = ProcrastinationDefeater()

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('data/daily_life_task_manager.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 description TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                 due_date DATETIME,
                 base_priority INTEGER DEFAULT 5,
                 dynamic_priority REAL,
                 energy_level INTEGER,
                 time_estimate INTEGER,
                 completed BOOLEAN DEFAULT FALSE,
                 completed_at DATETIME)''')
    conn.commit()
    conn.close()

def display_analytics():
    """Display analytics dashboard"""
    conn = sqlite3.connect('data/daily_life_task_manager.db')

    st.subheader("📊 Task Analytics")

    try:
        # Task completion rate
        completed_tasks_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = TRUE").fetchone()[0]
        total_tasks_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        completion_rate = (completed_tasks_count / total_tasks_count) * 100 if total_tasks_count > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", total_tasks_count)
        with col2:
            st.metric("Completed Tasks", completed_tasks_count)
        with col3:
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

        # Priority distribution chart
        st.write("### Priority Distribution")
        priority_data = conn.execute("""
            SELECT
                CASE
                    WHEN dynamic_priority > 7 THEN 'High'
                    WHEN dynamic_priority > 4 THEN 'Medium'
                    ELSE 'Low'
                END as priority_level,
                COUNT(*) as count
            FROM tasks
            GROUP BY priority_level
        """).fetchall()

        if priority_data:
            fig = px.pie(
                names=[row[0] for row in priority_data],
                values=[row[1] for row in priority_data],
                title="Task Priority Distribution"
            )
            st.plotly_chart(fig)
        else:
            st.info("No task data available for analytics")

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
    finally:
        conn.close()

def display_task_dashboard(energy, time, location):
    """Display the main task dashboard"""
    conn = sqlite3.connect('data/daily_life_task_manager.db')

    # Add new task form
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title*", help="Required field")
            description = st.text_area("Description")
        with col2:
            due_date_input = st.date_input("Due Date", datetime.now() + timedelta(days=1))
            base_priority = st.slider("Base Priority", 1, 10, 5)
            time_estimate = st.number_input("Time Estimate (minutes)", 5, 240, 30)

        if st.form_submit_button("Add Task"):
            if title:
                dynamic_priority = priority_engine.calculate_dynamic_priority(
                    base_priority, due_date_input, time_estimate
                )
                Task.create(conn, title, description, due_date_input,
                          base_priority, dynamic_priority, time_estimate)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.warning("Please enter a task title")

    # Display tasks
    st.subheader("Your Context-Optimized Task List")
    tasks = Task.get_all(conn)

    if not tasks:
        st.info("No tasks yet! Add your first task above.")
    else:
        ranked_tasks = context_analyzer.rank_tasks(tasks, energy, time, location)

        for task_data in ranked_tasks:
            display_task_card(conn, task_data, energy, time)

    conn.close()

def display_task_card(conn, task_data, energy, time):
    """Display an individual task card"""
    task = Task(*task_data) # Create a Task object from the tuple
    with st.container():
        col1, col2 = st.columns([0.8, 0.2])

        with col1:
            # Dynamic priority indicator
            priority_color = "#ff4b4b" if task.dynamic_priority > 7 else "#ffa700" if task.dynamic_priority > 4 else "#00cc66"
            due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No deadline'

            st.markdown(
                f"<h3 style='color:{priority_color}'>"
                f"{'✅ ' if task.completed else ''}{task.title}</h3>"
                f"<p><b>Priority:</b> {task.dynamic_priority:.1f}</p>"
                f"<p><b>Due:</b> {due_date_str}</p>"
                f"<p>{task.description or 'No description'}</p>",
                unsafe_allow_html=True
            )

            # Micro-progress tracker
            if not task.completed:
                with st.expander("Breakdown into micro-steps"):
                    micro_steps = procrastination_defeater.generate_micro_steps(task)
                    for i, step in enumerate(micro_steps):
                        st.checkbox(step, key=f"micro_{task.id}_{i}")


        with col2:
            if not task.completed:
                if st.button("✅ Complete", key=f"complete_{task.id}"):
                    Task.mark_complete(conn, task.id)
                    st.rerun()
            if st.button("🗑️ Delete", key=f"delete_{task.id}"):
                Task.delete(conn, task.id)
                st.rerun()


def main():
    """Main application function"""
    st.set_page_config(
        page_title="Daily Life Task Manager",
        page_icon="✅",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .st-emotion-cache-1y4p8pa {padding: 2rem 1rem 10rem;}
        .stButton button {width: 100%;}
        .task-card {border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)

    st.title("✅ Daily Life Task Manager")
    st.markdown("#### Your intelligent, context-aware productivity companion")

    init_db()

    # User context input
    with st.sidebar:
        st.header("⚡ Your Current Context")
        current_energy = st.slider("Energy Level (1-10)", 1, 10, 7)
        available_time = st.number_input("Available Time (minutes)", 5, 240, 30)
        current_location = st.selectbox("Location", ["Home", "Office", "Commuting", "Other"])

    # Main app sections
    tab1, tab2, tab3 = st.tabs(["📋 Task Dashboard", "📊 Analytics", "🚀 Productivity Tools"])

    with tab1:
        display_task_dashboard(current_energy, available_time, current_location)

    with tab2:
        display_analytics()

    with tab3:
        procrastination_defeater.display_anti_procrastination_tools()

if __name__ == "__main__":
    main()