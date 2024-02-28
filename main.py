import streamlit as st
from datetime import datetime, date
import time
import pandas as pd
import functions as func

func.check_necessary_files_exist()


def warning_operation():
    if "warning_days_left" in st.session_state:
        days_left = st.session_state["warning_days_left"]

        if days_left != 0:
            warning_color = st.session_state["warning_color"]
            func.add_warn(days_left, warning_color)

    if "warning_table" in st.session_state:
        edited_rows = st.session_state["warning_table"]["edited_rows"]
        if edited_rows:
            for index, changes in edited_rows.items():

                if changes["Delete"]:
                    warn_list = [[item['days_left'], item['warn_color'], False] for item in func.get_warns_list()]
                    func.delete_warn(warn_list[index][0])


def todos_table_operation():
    if "todos_table" in st.session_state:
        todos_list = func.get_parse_todos_list()

        add_rows = st.session_state["todos_table"]["added_rows"]
        edited_rows = st.session_state["todos_table"]["edited_rows"]
        deleted_rows = st.session_state["todos_table"]["deleted_rows"]

        if add_rows:
            for item in add_rows:
                due_time = func.convert_string_to_unix(item['Due'], datetime_format="%Y-%m-%d")
                func.add_todo(item['Title'], int(time.time()), due_time)

        if edited_rows:
            for item in edited_rows:

                if 'Due' in edited_rows[item]:
                    due_time = func.convert_string_to_unix(edited_rows[item]['Due'])
                else:
                    due_time = func.convert_string_to_unix(todos_list[item]['due_time'])

                if 'Title' in edited_rows[item]:
                    title = edited_rows[item]['Title']
                else:
                    title = todos_list[item]['title']

                if 'C.' in edited_rows[item]:
                    func.add_to_completed(todos_list[item]['id'], int(time.time()))
                else:
                    func.edit_todo(todos_list[item]['id'], title, due_time)

        if deleted_rows:
            for item in deleted_rows:
                func.delete_from_todo(todos_list[item]['id'])


def completed_table_operation():
    if "completed_table" in st.session_state:

        completed_list = func.get_parse_completed_list()

        edited_rows = st.session_state["completed_table"]["edited_rows"]

        if edited_rows:
            for item in edited_rows:
                if 'Back to todos' in edited_rows[item]:
                    func.back_to_todo_from_completed(completed_list[item]['id'])


todos_table_operation()
completed_table_operation()

st.set_page_config(
    page_title="TODO WEB APP",
    page_icon="📝",
    layout="centered",
)

current_datetime = datetime.now()
now_date = date(current_datetime.year, current_datetime.month, current_datetime.day)

st.markdown("<h1 style='text-align: center;'>TODO WEB APP</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'>" + current_datetime.strftime("%d %b %Y") + "</div>",
            unsafe_allow_html=True)

warning_col, reset_app_col = st.columns(2)

with warning_col:
    with st.expander("Warnings"):
        st.color_picker("Warning Color", key="warning_color")

        st.number_input("Days left", key="warning_days_left", min_value=0, max_value=364, on_change=warning_operation())

        df = pd.DataFrame([[item['days_left'], item['warn_color'], False] for item in func.get_warns_list()],
                          columns=["Days Left", "Warning Color", "Delete"])
        df = df.style.map(func.highlight_cells, subset=["Warning Color"])
        st.data_editor(df,
                       column_config={
                           "Days left": st.column_config.TextColumn(
                               disabled=True,
                           ),
                           "Warning Color": st.column_config.TextColumn(
                               disabled=True,
                           ),
                       },
                       hide_index=True,
                       key="warning_table")

with (reset_app_col):
    with st.expander("Reset App"):
        st.write("This is irreversible and will delete all saved data.")

        if st.button("Reset", key="reset_app", type="primary"):
            st.checkbox("Are you sure ?", key="reset_app_confirm")

        if st.session_state.get("reset_app_confirm", False):
            func.remove_directory()
            st.write("Resetting the app...")
            st.experimental_rerun()

todos_tab, completed_tab = st.tabs(["Todos", "Completed"])

with todos_tab:
    todos_df = pd.DataFrame(func.table_todos_list(), columns=[" ", "Title", "Creation", "Due", "C."])
    todos_df = todos_df.style.apply(func.highlight_todo_rows, subset=" ")

    st.data_editor(
        todos_df,
        column_config={
            " ": st.column_config.TextColumn(
                disabled=True,
            ),
            "Title": st.column_config.TextColumn(
                width="large",
                required=True
            ),
            "Creation": st.column_config.TextColumn(
                disabled=True,
                default=datetime.now().strftime("%Y-%m-%d")
            ),
            "Due": st.column_config.DateColumn(
                format="Y-MM-DD",
                default=now_date,
                min_value=now_date
            ),
            "C.": st.column_config.CheckboxColumn(
                default=False
            )
        },
        hide_index=True,
        num_rows="dynamic",
        key="todos_table"
    )

with completed_tab:
    df = pd.DataFrame(func.table_completed_list(), columns=["Title", "Due", "Complete In", "Back to todos"])
    st.data_editor(
        df,
        column_config={
            "Title": st.column_config.TextColumn(
                width="large",
                disabled=True
            ),
            "Due": st.column_config.TextColumn(
                disabled=True,
            ),
            "Complete In": st.column_config.TextColumn(
                disabled=True,
            )
        },
        hide_index=True,
        key="completed_table"
    )

footer = """
<div class="st-emotion-cache-h5rgaw ea3mdgi1" style="text-align:center;margin-top:30px">
    &#169;2024 Meysam Davoudi, All Rights Reserved.
    <a href="https://github.com/Meysam-Davoudi/todo-app-streamlit" target="_blank" style="text-decoration:none;">
        (GITHUB)
    </a>
</div>
"""

# Display the footer
st.markdown(footer, unsafe_allow_html=True)
