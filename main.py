import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
import plotly.express as px

from services.task import Task
from services.priority_engine import PriorityEngine
from services.context_analyzer import ContextAnalyzer
from services.procrastination_defeater import ProcrastinationDefeater

# Initialize components
priority_engine = PriorityEngine()
context_analyzer = ContextAnalyzer()
procrastination_defeater = ProcrastinationDefeater()


os.makedirs("data", exist_ok=True)

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('data/daily_life_task_manager.db')
    c = conn.cursor()
    # This schema with energy_level
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
        st.subheader("➕ Add a New Task")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title*", help="Required field")
            description = st.text_area("Description")
        with col2:
            due_date_input = st.date_input("Due Date", datetime.now().date() + timedelta(days=1))
            base_priority = st.slider("Base Priority (1-10)", 1, 10, 5)
            time_estimate = st.number_input("Time Estimate (minutes)", min_value=5, max_value=240, value=30, step=5)
            energy_level_input = st.slider("Required Energy (1-10)", 1, 10, 5)


        if st.form_submit_button("Add Task"):
            if title:
                # Convert date object to datetime object for consistency
                due_date_dt = datetime.combine(due_date_input, datetime.min.time())
                dynamic_priority = priority_engine.calculate_dynamic_priority(
                    base_priority, due_date_dt, time_estimate
                )
                # --- FIX: Pass the energy_level_input to the create function ---
                Task.create(conn, title, description, due_date_dt,
                          base_priority, dynamic_priority, time_estimate, energy_level_input)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.warning("Please enter a task title")

    # Display tasks
    st.subheader("✅ Your Context-Optimized Task List")
    tasks = Task.get_all(conn)

    if not tasks:
        st.info("No tasks yet! Add your first task above.")
    else:
        # The context analyzer now needs the full Task object
        ranked_tasks = context_analyzer.rank_tasks(tasks, energy, time, location)

        for task in ranked_tasks:
            display_task_card(conn, task, energy, time)

    conn.close()

def display_task_card(conn, task, energy, time):
    """Display an individual task card"""
    # No need to create a new object, 'task' is already a Task instance
    with st.container():
        col1, col2 = st.columns([0.8, 0.2])

        with col1:
            # Dynamic priority indicator
            priority_color = "#ff4b4b" if task.dynamic_priority > 7 else "#ffa700" if task.dynamic_priority > 4 else "#00cc66"
            
            # Safely format due_date
            due_date_str = task.due_date.strftime('%Y-%m-%d') if isinstance(task.due_date, datetime) else 'No deadline'

            st.markdown(
                f"<h3 style='color:{priority_color};'>"
                f"{'✅ ' if task.completed else ''}{task.title}</h3>"
                f"<p><b>Priority:</b> {task.dynamic_priority:.1f} | "
                f"<b>Energy Needed:</b> {task.energy_level} | "
                f"<b>Time:</b> {task.time_estimate} min</p>"
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
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .stButton button {width: 100%;}
        .st-emotion-cache-1y4p8pa { padding-top: 2rem; }
        .st-emotion-cache-z5fcl4 { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

    st.title("Daily Life Task Manager")
    st.markdown("#### Your intelligent, context-aware productivity companion")

    init_db()

    # User context input
    with st.sidebar:
        st.header("⚡ Your Current Context")
        current_energy = st.slider("Your Energy Level (1-10)", 1, 10, 7)
        available_time = st.number_input("Available Time (minutes)", min_value=5, max_value=300, value=60, step=5)
        current_location = st.selectbox("Your Location", ["Home", "Office", "Commuting", "Other"])

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
