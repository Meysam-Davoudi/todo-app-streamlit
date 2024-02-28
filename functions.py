import os
from shutil import rmtree
from pathlib import Path
from datetime import datetime, timezone, timedelta


def column_separator():
    separator = "^&$&^"
    return separator


def convert_string_to_unix(date_string, datetime_format="%Y-%m-%d"):
    # Convert the string date to a Unix timestamp
    date_obj = datetime.strptime(date_string, datetime_format).replace(tzinfo=timezone.utc)
    unix_timestamp = date_obj.timestamp()

    return int(unix_timestamp)


def convert_unix_to_string(unix_timestamp, datetime_format="%Y-%m-%d"):
    # Convert the Unix timestamp to datetime string
    date_obj = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
    date_string = date_obj.strftime(datetime_format)

    return date_string


def list_sort(input_list, column, order='ASC', integer_column=False):
    reverse = False
    if order.upper() == 'DESC':
        reverse = True

    if integer_column:
        sorted_list = sorted(input_list, key=lambda x: int(x[column]), reverse=reverse)
    else:
        sorted_list = sorted(input_list, key=lambda x: x[column], reverse=reverse)

    return sorted_list


def make_row_string(todo_id, title, creation, due_time, completed_time=''):
    row_string = f"{todo_id}{column_separator()}{title}{column_separator()}{creation}{column_separator()}{due_time}"

    if completed_time != '':
        row_string += f"{column_separator()}{completed_time}"

    return row_string


def get_settings():
    with open(get_path('setting'), "r") as file:
        settings = file.readlines()

    settings = [item.strip("\n") for item in settings]

    return settings


def update_settings(new_settings):
    settings = [item + "\n" for item in new_settings]

    with open(get_path('setting'), "w") as file:
        file.writelines(settings)


def get_warns_list():
    settings = get_settings()
    warns_list = []

    for item in settings:
        if item.startswith("warn:"):
            warn = item[5:].split(column_separator())
            warns_list.append({"days_left": warn[0], "warn_color": warn[1]})

    warns_list = list_sort(warns_list, "days_left", "desc", True)
    return warns_list


def add_warn(days_left, warning_color):
    settings = get_settings()
    exist_warn = check_warn_exist(days_left)

    if exist_warn:
        for index, item in enumerate(settings):
            if item.startswith("warn:"):
                warn = item[5:].split(column_separator())
                if int(warn[0]) == int(days_left):
                    settings[index] = f"warn:{days_left}{column_separator()}{warning_color}"

    else:
        new_warn = f"warn:{days_left}{column_separator()}{warning_color}"
        settings.append(new_warn)

    update_settings(settings)


def check_warn_exist(days_left):
    exist = False
    warns_list = get_warns_list()

    for warn in warns_list:
        if int(warn['days_left']) == int(days_left):
            exist = True

    return exist


def delete_warn(days_left):
    settings = get_settings()

    for index, item in enumerate(settings):
        if item.startswith("warn:"):
            warn = item[5:].split(column_separator())
            if int(warn[0]) == int(days_left):
                settings.pop(index)

    update_settings(settings)


def get_new_todo_id():
    last_id = 0
    settings = get_settings()

    for index, item in enumerate(settings):
        if item.startswith("lastTodoID="):
            last_id = int(item[11:])
            settings[index] = f"lastTodoID={last_id + 1}"

    update_settings(settings)

    new_id = last_id + 1
    return new_id


def get_todos_list():
    with open(get_path('todos'), "r") as file:
        todos = file.readlines()

    todos = [item.strip("\n") for item in todos]

    return todos


def get_parse_todos_list():
    todos_list = get_todos_list()
    parse_todos = []

    for item in todos_list:
        todo = item.split(column_separator())

        creation = convert_unix_to_string(todo[2])
        due_time = convert_unix_to_string(todo[3])

        parse_item = {"id": todo[0], "title": todo[1], "creation": creation, "due_time": due_time,
                      "unix_creation": todo[2], "unix_due_time": todo[3]}
        parse_todos.append(parse_item)

    parse_todos = list_sort(parse_todos, "unix_due_time", integer_column=True)
    return parse_todos


def get_todo_by_id(todo_id):
    result = {}
    todos_list = get_parse_todos_list()
    for item in todos_list:
        if int(item['id']) == int(todo_id):
            result = item

    return result


def update_todos_list(new_todos):
    todos = [item + "\n" for item in new_todos]

    with open(get_path('todos'), "w") as file:
        file.writelines(todos)


def add_todo(title, creation, due_time):
    todos = get_todos_list()
    todo_id = get_new_todo_id()

    todos.append(make_row_string(todo_id, title, creation, due_time))

    update_todos_list(todos)


def edit_todo(todo_id, new_title, new_due_time):
    todos_list = get_todos_list()

    for index, item in enumerate(todos_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            todos_list[index] = make_row_string(todo_id=todo[0], title=new_title,
                                                creation=todo[2], due_time=new_due_time)

    update_todos_list(todos_list)


def delete_from_todo(todo_id):
    todos_list = get_todos_list()

    for index, item in enumerate(todos_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            todos_list.pop(index)

    update_todos_list(todos_list)


def get_completed_list():
    with open(get_path('completed'), "r") as file:
        completed = file.readlines()

    completed = [item.strip("\n") for item in completed]

    return completed


def get_parse_completed_list():
    completed_list = get_completed_list()
    parse_completed = []

    for item in completed_list:
        todo = item.split(column_separator())

        creation = convert_unix_to_string(todo[2])
        due_time = convert_unix_to_string(todo[3])
        completed_time = convert_unix_to_string(todo[4])

        parse_item = {"id": todo[0], "title": todo[1], "creation": creation, "due_time": due_time,
                      "completed_time": completed_time, "unix_creation": todo[2], "unix_due_time": todo[3],
                      "unix_completed_time": todo[4]}

        parse_completed.append(parse_item)

    parse_completed = list_sort(parse_completed, "unix_due_time", integer_column=True)
    return parse_completed


def get_completed_todo_by_id(todo_id):
    result = {}
    completed_list = get_parse_completed_list()
    for item in completed_list:
        if int(item['id']) == int(todo_id):
            result = item

    return result


def update_completed_list(new_list):
    completed_list = [item + "\n" for item in new_list]

    with open(get_path('completed'), "w") as file:
        file.writelines(completed_list)


def add_to_completed(todo_id, completed_time):
    todos_list = get_todos_list()
    completed_list = get_completed_list()

    for index, item in enumerate(todos_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            completed_list.append(make_row_string(todo_id=todo[0], title=todo[1], creation=todo[2],
                                                  due_time=todo[3], completed_time=completed_time))

    update_completed_list(completed_list)
    delete_from_todo(todo_id)


def edit_completed_todo(todo_id, new_title, new_due_time):
    completed_list = get_completed_list()

    for index, item in enumerate(completed_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            completed_list[index] = make_row_string(todo_id=todo[0], title=new_title, creation=todo[2],
                                                    due_time=new_due_time, completed_time=todo[4])

    update_completed_list(completed_list)


def back_to_todo_from_completed(todo_id):
    todos_list = get_todos_list()
    completed_list = get_completed_list()

    for index, item in enumerate(completed_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            todos_list.append(make_row_string(todo_id=todo[0], title=todo[1], creation=todo[2], due_time=todo[3]))

    update_todos_list(todos_list)
    delete_from_completed(todo_id)


def delete_from_completed(todo_id):
    completed_list = get_completed_list()

    for index, item in enumerate(completed_list):
        todo = item.split(column_separator())
        if int(todo[0]) == int(todo_id):
            completed_list.pop(index)

    update_completed_list(completed_list)


def table_todos_list():
    todos = get_parse_todos_list()
    todos_value = [[
        item['id'],
        item['title'],
        item['creation'],
        datetime.strptime(item['due_time'], "%Y-%m-%d"),
        False
    ]
        for item in todos]
    return todos_value


def table_completed_list():
    completed = get_parse_completed_list()
    completed_value = [[
        item['title'],
        item['due_time'],
        item['completed_time'],
        False
    ]
        for item in completed]
    return completed_value


def get_opposite_color(color):
    # Convert the color to RGB values
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    # Calculate the relative luminance (brightness) of the color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Determine the appropriate color based on luminance
    if luminance > 0.5:
        return "#000000"
    else:
        return "#FFFFFF"


def highlight_cells(color):
    return f"background-color: {color}; color: {get_opposite_color(color)};"


def table_todo_warn_color():
    todos_list = get_parse_todos_list()
    warns_list = get_warns_list()
    row_colors = []
    row_index_list = []

    for w_index, warn in enumerate(warns_list):
        for index, item in enumerate(todos_list):
            warn_unix_timestamp = int(((datetime.now()) + timedelta(days=int(warn['days_left']))).timestamp())

            if int(item['unix_due_time']) <= warn_unix_timestamp:

                if index in row_index_list:
                    row_colors = [item for item in row_colors if item[0] != index]

                row_index_list.append(index)
                row_colors.append((index, warn['warn_color']))

    return row_colors


def highlight_todo_rows(rows):
    warn_colors = table_todo_warn_color()

    styles = [next((f"background-color: {warn_color}; color: {warn_color}" for warn_index, warn_color in warn_colors
                    if warn_index == row_index), "color: #FFFFFF")
              for row_index, row in enumerate(rows)]

    # second way
    # styles = ['color: #FFFFFF'] * len(rows)
    #
    # for index, row in enumerate(rows):
    #     for key, value in enumerate(warn_colors):
    #         if index == value[0]:
    #             styles[index] = f"background-color: {warn_colors[key][1]}; color: {warn_colors[key][1]}"

    return styles


def check_necessary_files_exist():
    directory = get_path('directory')
    todos = get_path('todos')
    completed = get_path('completed')
    setting = get_path('setting')

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(todos):
        with open(todos, "w") as file:
            file.write("")

    if not os.path.exists(completed):
        with open(completed, "w") as file:
            file.write("")

    if not os.path.exists(setting):
        with open(setting, "w") as file:
            file.write("lastTodoID=0\n")


def get_path(name):
    path = ''
    match name:
        case 'directory':
            root_directory = os.getcwd()
            subdirectory = "todo-app-data"

            # Create the full directory path
            path = os.path.join(root_directory, subdirectory)
        case 'todos':
            todos_file_name = "todos.db"
            path = os.path.join(get_path('directory'), todos_file_name)
        case 'completed':
            completed_file_name = "completed.db"
            path = os.path.join(get_path('directory'), completed_file_name)
        case 'setting':
            setting_file_name = "setting.db"
            path = os.path.join(get_path('directory'), setting_file_name)

    return path


def remove_directory():
    directory = Path(get_path('directory'))

    if os.path.exists(directory):
        try:
            if directory.is_dir():
                rmtree(directory)
        except OSError as e:
            pass
