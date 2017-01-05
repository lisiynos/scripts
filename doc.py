# ~*~ coding: utf-8 ~*~
# Генерация README.md по специально размеченным исходникам
# Добавьте doc.cmd в пути
import os
import re
import sys
import traceback
import unittest

PREFIX = u'//'
# Стандартный комментарий для документирования
PREFIX2 = u'///'

ROOT_DIR = '.\\'

extensions = [".cpp", ".c", ".h", ".hpp", ".java", ".md"]
special_files = ["pom.xml"]


def get_extension(file_name):
    return os.path.splitext(file_name)[1]


def lang(file_name):
    """
    Определение языка подсветки по имени файла
    :param file_name: имя файла
    """
    extension = get_extension(file_name)
    if extension in ['.cpp', '.c', '.h', '.hpp']:
        return 'cpp'
    if extension == '.java':
        return 'java'
    return "TODO: doc.py Сделать обработчик **" + extension + "**"


def is_header1(s):  # Подчёркивание заголовка 1
    return re.match('\\={3,}', s.strip())


def is_header2(s):  # Подчёркивание заголовка 2
    return re.match('\\-{3,}', s.strip())


def process_headers(prev, cur):
    if is_header1(cur):
        print('', file=themes)
        print(prev, file=themes)
        print('-' * len(prev), file=themes)
    if is_header2(cur):
        print("* " + prev, file=themes)


def parse(file_name):
    """
    :param file_name: имя файла
    :return:
    """
    code = False
    out = False
    cur = ""
    with open(file_name, "r", encoding="utf-8-sig") as f:
        for line in f:
            s = line.strip()
            if '//-->' in line:
                print('``` ' + lang(file_name))
                code = True
                out = True
                continue
            elif '//<--' in line:
                print('```')
                print()
                code = False
                out = True
                continue
            elif code:
                print(line.rstrip())
                out = True
                continue
            elif s.startswith(PREFIX2):
                prev = cur
                cur = s[len(PREFIX2):].strip()
                print(cur)
                process_headers(prev, cur)
                out = True
                continue
            elif s.startswith(PREFIX):
                prev = cur
                cur = s[len(PREFIX):].strip()
                print(cur)
                process_headers(prev, cur)
                out = True
                continue
    return out


def filename2link(filename):
    if filename.startswith(ROOT_DIR):
        filename = filename[len(ROOT_DIR):].strip()
    # Исправление разделителя каталогов (file separator) в путях
    filename = filename.replace("\\", "/")
    return '[' + filename + '](' + filename + ')'


# Предотвращение перезаписи README.md созданных не нами
HEADER = '<!-- doc.py -->'
README = "README.md"
FORCE_OVERWRITE = False

# Если очень нужно перезаписать, можно вызывать с ключом -force
for arg in sys.argv:
    if arg.lower() == "-force":
        FORCE_OVERWRITE = True

if __name__ == "__main__":
    if not FORCE_OVERWRITE and os.path.isfile(README):
        f = open(README, "r", encoding="utf-8")
        # Читаем заголовок файла
        header = f.readline().strip()
        f.close()
        if header.upper() != HEADER.upper():
            print(README + ' have not ' + HEADER + ' - EXIT!')
            exit(1)

    # Открываем README.md для записи
    sys.stdout = open(README, "w", encoding="utf-8")
    print(HEADER)

    # Открываем темы
    THEMES = "themes.md"
    if os.path.isfile(THEMES):
        themes = open(THEMES, "w", encoding="utf-8")
    else:
        themes = sys.stderr

    all_files = []
    for root, dirs, files in os.walk("."):
        for name in files:
            # Пропускаем сгенерированные файлы Qt
            if name.startswith('moc_'): continue
            if name.startswith('ui_'): continue
            # Пропускаем файлы в другой кодировке
            if "_cp866" in name: continue
            if "_win1251" in name: continue
            if (get_extension(name) in extensions) or (name in special_files):
                # Пропускаем готовые README.md
                if name.upper() == README.upper():
                    continue
                file_name = os.path.join(root, name)
                if file_name == '.\\README.md':
                    continue
                all_files.append(file_name)

    for file_name in sorted(all_files):
        # Markdown файлы просто передаём на выход не меняя
        if get_extension(file_name).lower() == ".md":
            prev = ""  # Предыдущая строка
            for line in open(file_name, 'r', encoding="utf-8"):
                cur = line.rstrip()  # Текущая строка
                print(cur)
                process_headers(prev, cur)
                prev = cur
            print()
            continue
        # Если были какие-то строчки из файла,
        # добавляем ссылку на файл
        try:
            if parse(file_name):
                print(filename2link(file_name))
                print()
        except:  # Ошибка разбора файла
            traceback.print_exc(file=sys.stderr)
            print("FILE: " + file_name, file=sys.stderr)

    themes.close()


class TestRating(unittest.TestCase):
    """ Модульные тесты """

    def test_filename2link(self):
        """ Разделение команды на участников """
        self.assertEquals('[main.cpp](main.cpp)', filename2link('.\main.cpp'))
        self.assertEquals('[a/b.cpp](a/b.cpp)', filename2link('.\\a\\b.cpp'))

    def test_headers(self):
        self.assertTrue(is_header1("===="))
        self.assertFalse(is_header1("="))
        self.assertFalse(is_header1("---"))
        self.assertFalse(is_header1("==2=="))
        self.assertTrue(is_header2("-------"))
