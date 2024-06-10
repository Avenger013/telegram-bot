import os


def read_file_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                return f.readlines()
        except UnicodeDecodeError:
            return []


def is_code_line(line, in_multiline_comment):
    stripped_line = line.strip()
    if not stripped_line or stripped_line.startswith('#'):
        return False, in_multiline_comment
    if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
        in_multiline_comment = not in_multiline_comment
        return False, in_multiline_comment
    if in_multiline_comment:
        return False, in_multiline_comment
    return True, in_multiline_comment


def count_code_lines_in_file(file_path):
    lines = read_file_lines(file_path)
    code_lines = 0
    in_multiline_comment = False
    for line in lines:
        is_code, in_multiline_comment = is_code_line(line, in_multiline_comment)
        if is_code:
            code_lines += 1
    return code_lines


def count_code_lines_in_directory(directory, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ['venv', 'env', '.venv', '__pycache__']

    total_lines = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_lines += count_code_lines_in_file(file_path)
    return total_lines


# def count_code_lines_in_directory(directory):
#     total_lines = 0
#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file.endswith('.py'):
#                 file_path = os.path.join(root, file)
#                 total_lines += count_code_lines_in_file(file_path)
#     return total_lines


def count_code_lines(target):
    if isinstance(target, list):
        return sum(count_code_lines_in_file(file) for file in target)
    elif isinstance(target, str) and os.path.isdir(target):
        return count_code_lines_in_directory(target)
    else:
        raise ValueError("Target must be a list of file paths or a directory path")


file_list = [
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\database\models.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\database\requests.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\__init__.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\admin_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\dz_2_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\dz_3_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\dz_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\last_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\lk_and_commands.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\start_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\student_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\routers\teacher_router.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\utils\commands.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\keyboard.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\middleware.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\scheduler.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\application\states.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\config.py',
    r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana\main.py'
]

total_code_lines = sum(count_code_lines_in_file(file) for file in file_list)
print('Всего строк кода в выбранных файлах:', total_code_lines)

project_directory = r'C:\Users\Rustam2.0\PycharmProjects\telegram-bot-nirvana'
total_code_lines_in_directory = count_code_lines(project_directory)
print('Всего строк кода во всей директории проекта:', total_code_lines_in_directory)
