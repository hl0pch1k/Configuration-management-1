import os
import pytest
import zipfile
from main import ShellEmulatorGUI

@pytest.fixture
def setup_virtual_fs(tmpdir):
    """
    Фикстура для создания временной виртуальной файловой системы.
    """
    temp_dir = tmpdir.mkdir("virtual_fs")

    # Создаем тестовую файловую систему
    filesystem_structure = {
        'README.txt': 'Добро пожаловать в виртуальную файловую систему!',
        'папка1': {
            'файл1.txt': 'Это содержимое файла 1 в папке1.',
            'файл2.txt': 'Это содержимое файла 2 в папке1.',
        },
        'папка2': {
            'под_папка1': {
                'файл3.txt': 'Это содержимое файла 3 в под_папка1.',
            },
            'под_папка2': {
                'файл4.txt': 'Это содержимое файла 4 в под_папка2.',
            },
        },
    }

    # Создаем файловую систему
    def create_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

    # Создаем структуру в temp_dir
    create_structure(str(temp_dir), filesystem_structure)

    # Создаем zip-архив
    archive_name = os.path.join(tmpdir, 'filesystem.zip')
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(
                    file_path,
                    os.path.relpath(file_path, temp_dir)
                )
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                zipf.write(
                    dir_path,
                    os.path.relpath(dir_path, temp_dir)
                )

    # Возвращаем путь к созданному архиву для использования в тестах
    return archive_name

@pytest.fixture
def app_with_virtual_fs(setup_virtual_fs):
    """
    Фикстура для инициализации приложения с тестовым архивом.
    """
    app = ShellEmulatorGUI()
    app.open_virtual_fs(setup_virtual_fs)
    yield app
    app.destroy()

def test_command_ls(app_with_virtual_fs):
    """
    Тест команды ls для отображения содержимого директории.
    """
    app_with_virtual_fs.command_entry.insert(0, "ls")
    app_with_virtual_fs.process_command()
    output = app_with_virtual_fs.output_text.get("1.0", "end")
    assert "README.txt" in output
    assert "папка1" in output
    assert "папка2" in output

def test_command_cd(app_with_virtual_fs):
    """
    Тест команды cd для перехода в директорию и возврата в корень.
    """
    app_with_virtual_fs.command_entry.insert(0, "cd папка1")
    app_with_virtual_fs.process_command()
    assert app_with_virtual_fs.current_dir == "/папка1"

    app_with_virtual_fs.command_entry.insert(0, "cd ..")
    app_with_virtual_fs.process_command()
    assert app_with_virtual_fs.current_dir == "/"

def test_command_cat(app_with_virtual_fs):
    """
    Тест команды cat для отображения содержимого файла.
    """
    app_with_virtual_fs.command_entry.insert(0, "cat README.txt")
    app_with_virtual_fs.process_command()
    output = app_with_virtual_fs.output_text.get("1.0", "end")
    assert "Добро пожаловать в виртуальную файловую систему!" in output

def test_command_chmod(app_with_virtual_fs):
    """
    Тест команды chmod для изменения прав доступа.
    """
    app_with_virtual_fs.command_entry.insert(0, "chmod папка1/файл1.txt 644")
    app_with_virtual_fs.process_command()
    output = app_with_virtual_fs.output_text.get("1.0", "end")
    assert "Права на файл 'папка1/файл1.txt' изменены на 644." in output

def test_command_tree(app_with_virtual_fs):
    """
    Тест команды tree для отображения структуры директорий.
    """
    app_with_virtual_fs.command_entry.insert(0, "tree")
    app_with_virtual_fs.process_command()
    output = app_with_virtual_fs.output_text.get("1.0", "end")
    assert "папка1/" in output
    assert "папка2/" in output
    assert "под_папка1/" in output

def test_command_return(app_with_virtual_fs):
    """
    Тест команды return для возврата в корень виртуальной файловой системы.
    """
    app_with_virtual_fs.command_entry.insert(0, "cd папка1")
    app_with_virtual_fs.process_command()
    assert app_with_virtual_fs.current_dir == "/папка1"
    app_with_virtual_fs.command_entry.insert(0, "return")
    app_with_virtual_fs.process_command()
    assert app_with_virtual_fs.current_dir == "/"

def test_command_cd_invalid(app_with_virtual_fs):
    """
    Тест обработки ошибки при переходе в несуществующую директорию.
    """
    app_with_virtual_fs.command_entry.insert(0, "cd несуществующая_папка")
    app_with_virtual_fs.process_command()
    output = app_with_virtual_fs.output_text.get("1.0", "end")
    assert "Ошибка: Директория 'несуществующая_папка' не найдена или доступ запрещен." in output