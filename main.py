import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox


class ShellEmulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shell Emulator")
        self.geometry("1200x600")

        # Используем стиль ttk
        style = ttk.Style()
        style.theme_use('aqua')  # Используем тему macOS

        # Основной вывод для команд
        self.output_frame = ttk.Frame(self)
        self.output_frame.pack(side='left', expand=True, fill='both', padx=10, pady=10)

        self.output_text = tk.Text(
            self.output_frame, wrap='word', font=('Arial', 12), highlightthickness=0, bd=0
        )
        self.output_text.pack(expand=True, fill='both')

        # Нижняя рамка для ввода команд и кнопок
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        # Поле ввода команды
        self.command_entry = ttk.Entry(
            self.bottom_frame, width=30
        )
        self.command_entry.grid(row=0, column=0, padx=5, pady=5, sticky='we')

        # Позволяем нажатие Enter для выполнения команды
        self.command_entry.bind('<Return>', lambda event: self.process_command())

        # Кнопка выполнения команды
        self.run_button = ttk.Button(
            self.bottom_frame, text="Run Command", command=self.process_command
        )
        self.run_button.grid(row=0, column=1, padx=5)

        # Кнопка выхода
        self.exit_button = ttk.Button(
            self.bottom_frame, text="Exit", command=self.close_emulator
        )
        self.exit_button.grid(row=0, column=2, padx=5)

        # Позволяем command_entry растягиваться
        self.bottom_frame.columnconfigure(0, weight=1)

        # Рамка для кнопок и истории команд справа
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(side="right", padx=10, pady=10, fill='both', expand=True)

        # Создаем кнопки для команд
        self.create_command_buttons()

        # Разделитель между кнопками и историей команд
        separator = ttk.Separator(self.buttons_frame, orient='horizontal')
        separator.grid(row=7, column=0, columnspan=2, sticky='we', pady=10)

        # Настраиваем веса
        self.buttons_frame.grid_rowconfigure(8, weight=1)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        # Рамка для истории команд
        self.history_frame = ttk.Frame(self.buttons_frame)
        self.history_frame.grid(row=8, column=0, columnspan=2, sticky='nsew')

        # Заголовок истории команд
        self.history_label = ttk.Label(
            self.history_frame, text="История команд", font=('Arial', 14)
        )
        self.history_label.pack(pady=(0, 5))

        # Окно истории команд
        self.command_history_text = tk.Text(
            self.history_frame, wrap='word', font=('Arial', 12), highlightthickness=0, bd=0
        )
        self.command_history_text.pack(expand=True, fill='both')
        self.command_history_text.insert(tk.END, "")
        self.command_history_text.config(state=tk.DISABLED)

        # Инициализируем текущую виртуальную директорию
        self.current_dir = '/'  # Начинаем с корня виртуальной ФС
        self.root_dir = None  # Корневая директория

    def create_command_buttons(self):
        """Создаем кнопки для основных команд с подсказками"""
        commands = [
            ("ls", "Показать содержимое директории", self.insert_command_ls),
            ("cd", "Перейти в другую директорию", self.insert_command_cd),
            ("cat", "Показать содержимое файла", self.insert_command_cat),
            ("chmod", "Изменить права файла", self.insert_command_chmod),
            ("tree", "Показать структуру каталогов в виде дерева", self.insert_command_tree),
            ("return", "Вернуться в начальную директорию", self.insert_command_return),
            ("exit", "Выйти из эмулятора", self.insert_command_exit)
        ]

        for index, (cmd, tooltip, command_func) in enumerate(commands):
            button = ttk.Button(
                self.buttons_frame, text=cmd, command=command_func, width=10
            )
            button.grid(row=index, column=0, padx=5, pady=5, sticky="w")

            # Подсказка к кнопке
            button_tooltip = ttk.Label(
                self.buttons_frame, text=tooltip, anchor='w', width=35
            )
            button_tooltip.grid(row=index, column=1, padx=5, pady=5, sticky='w')

    def insert_command_ls(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "ls")

    def insert_command_cd(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "cd ")

    def insert_command_cat(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "cat ")

    def insert_command_chmod(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "chmod ")

    def insert_command_tree(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "tree")

    def insert_command_return(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "cd /")  # Возвращаемся в корень виртуальной ФС

    def insert_command_exit(self):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, "exit")

    def open_virtual_fs(self, archive_path):
        """Открываем архив виртуальной файловой системы"""
        self.output_text.insert(tk.END, f"Текущая рабочая директория: {os.getcwd()}\n")
        self.output_text.insert(tk.END, f"Путь к архиву: {os.path.abspath(archive_path)}\n")
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall('virtual_fs')
        self.root_dir = os.path.abspath('virtual_fs')
        self.current_dir = '/'  # Начинаем с корневой виртуальной директории

    def process_command(self):
        command_line = self.command_entry.get()
        command_parts = command_line.strip().split()

        if not command_parts:
            return

        command = command_parts[0]

        # Добавляем введенную команду в историю
        self.command_history_text.config(state=tk.NORMAL)
        self.command_history_text.insert(tk.END, command_line + "\n")
        self.command_history_text.config(state=tk.DISABLED)

        if command == 'ls':
            path = command_parts[1] if len(command_parts) > 1 else '.'
            self.command_ls(path)
            self.output_text.insert(
                tk.END, "\n# Используйте 'cd <папка>' для перехода в другую директорию.\n"
            )
        elif command == 'cd':
            path = " ".join(command_parts[1:]) if len(command_parts) > 1 else '/'
            self.command_cd(path)
            self.output_text.insert(
                tk.END, f"\n# Текущая директория: {self.current_dir}. Введите 'ls' для просмотра содержимого.\n"
            )
        elif command == 'cat':
            filename = " ".join(command_parts[1:]) if len(command_parts) > 1 else None
            if filename:
                self.command_cat(filename)
                self.output_text.insert(
                    tk.END, "\n# Вы можете прочитать другой файл с помощью 'cat <имя файла>'.\n"
                )
            else:
                self.output_text.insert(tk.END, "Использование: cat <имя файла>\n")
        elif command == 'exit':
            self.output_text.insert(tk.END, "\n# Выход из эмулятора...\n")
            self.close_emulator()
        elif command == 'chmod':
            if len(command_parts) == 3:
                self.command_chmod(command_parts[1], command_parts[2])
                self.output_text.insert(
                    tk.END, "\n# Права изменены. Используйте 'ls -l' для проверки прав.\n"
                )
            else:
                self.output_text.insert(tk.END, "Использование: chmod <файл> <права>\n")
        elif command == 'tree':
            path = command_parts[1] if len(command_parts) > 1 else '.'
            self.command_tree(path)
            self.output_text.insert(
                tk.END, "\n# Это структура каталогов. Используйте 'cd <папка>' для навигации.\n"
            )
        else:
            self.output_text.insert(tk.END, f"Неизвестная команда: {command}\n")

        self.command_entry.delete(0, tk.END)

    def resolve_virtual_path(self, path):
        """Разрешает виртуальный путь относительно текущей виртуальной директории"""
        # Если путь абсолютный
        if path.startswith('/'):
            virtual_path = os.path.normpath(path)
        else:
            virtual_path = os.path.normpath(os.path.join(self.current_dir, path))

        # Предотвращаем выход за пределы виртуальной ФС
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path

        return virtual_path

    def resolve_real_path(self, virtual_path):
        """Преобразует виртуальный путь в реальный путь в файловой системе"""
        real_path = os.path.normpath(os.path.join(self.root_dir, virtual_path.lstrip('/')))

        # Проверяем, что путь не выходит за пределы корневой директории
        if not os.path.commonpath([self.root_dir, real_path]) == self.root_dir:
            return None

        return real_path

    def command_ls(self, path):
        virtual_path = self.resolve_virtual_path(path)
        real_path = self.resolve_real_path(virtual_path)
        if real_path and os.path.isdir(real_path):
            files = os.listdir(real_path)
            for file in files:
                self.output_text.insert(tk.END, f"{file}\n")
        else:
            self.output_text.insert(tk.END, f"Ошибка: Директория '{path}' не найдена.\n")

    def command_cd(self, path):
        virtual_path = self.resolve_virtual_path(path)
        real_path = self.resolve_real_path(virtual_path)
        if real_path and os.path.isdir(real_path):
            self.current_dir = virtual_path
            # Не выводим сообщения о переходе и текущей виртуальной директории
        else:
            self.output_text.insert(tk.END, f"Ошибка: Директория '{path}' не найдена или доступ запрещен.\n")

    def command_cat(self, filename):
        virtual_path = self.resolve_virtual_path(filename)
        real_path = self.resolve_real_path(virtual_path)
        if real_path and os.path.isfile(real_path):
            try:
                with open(real_path, 'r') as file:
                    content = file.read()
                    self.output_text.insert(tk.END, content + "\n")
            except Exception as e:
                self.output_text.insert(tk.END, f"Ошибка при чтении файла '{filename}': {e}\n")
        else:
            self.output_text.insert(tk.END, f"Ошибка: Файл '{filename}' не найден.\n")

    def command_chmod(self, file, mode):
        virtual_path = self.resolve_virtual_path(file)
        real_path = self.resolve_real_path(virtual_path)
        if real_path and os.path.exists(real_path):
            try:
                mode_int = int(mode, 8)
                os.chmod(real_path, mode_int)
                self.output_text.insert(tk.END, f"Права на файл '{file}' изменены на {mode}.\n")
            except ValueError:
                self.output_text.insert(
                    tk.END,
                    "Ошибка: Неправильный формат прав. Используйте восьмеричное значение (например, 755).\n"
                )
            except Exception as e:
                self.output_text.insert(tk.END, f"Ошибка при изменении прав файла '{file}': {e}\n")
        else:
            self.output_text.insert(tk.END, f"Ошибка: Файл или директория '{file}' не найдены.\n")

    def command_tree(self, path):
        virtual_path = self.resolve_virtual_path(path)
        real_path = self.resolve_real_path(virtual_path)
        if real_path and os.path.isdir(real_path):
            for root, dirs, files in os.walk(real_path):
                level = os.path.relpath(root, real_path).count(os.sep)
                indent = ' ' * 4 * level
                self.output_text.insert(tk.END, f"{indent}{os.path.basename(root)}/\n")
                subindent = ' ' * 4 * (level + 1)
                for file in files:
                    self.output_text.insert(tk.END, f"{subindent}{file}\n")
        else:
            self.output_text.insert(tk.END, f"Ошибка: Директория '{path}' не найдена.\n")

    def close_emulator(self):
        """Метод выхода из эмулятора"""
        if messagebox.askokcancel("Выход", "Вы хотите выйти из эмулятора?"):
            self.destroy()


# Создаем GUI приложение
def main():
    app = ShellEmulatorGUI()

    # Открываем архив виртуальной файловой системы
    archive_path = 'filesystem.zip'  # Укажите путь к вашему архиву
    app.open_virtual_fs(archive_path)

    app.mainloop()


if __name__ == "__main__":
    main()