# ~*~ coding: utf-8 ~*~
# Code Blocks project files processing
import glob
import os
import re
from os import remove, close
from shutil import move
from tempfile import mkstemp
from time import sleep


def subdirs(dir_name='.'):  # Все подкаталоги заданного каталога
    return [name for name in os.listdir(dir_name) if os.path.isdir(dir_name + os.path.sep + name)]


# Здесь можно вписать каталог в котором будет запущена обработка файлов проекта CodeBlocks
BASE_DIR = os.getcwd()  # "C:\\cpp\\04"
sd = subdirs(BASE_DIR)


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w', encoding='utf-8') as new_file:
        with open(file_path, encoding='utf-8') as old_file:
            for line in old_file:
                new_file.write(re.sub(pattern, subst, line))
    close(fh)
    # Remove original file
    while True:
        try:  # Try to remove origin file
            remove(file_path)
            break
        except:
            # If fail, try to wait and repeat
            print('waiting...')
            sleep(0.1)
    # Move new file
    move(abs_path, file_path)


# Заходим в подкаталог и находим .cbp файл
def process_dir(dir_name):
    path = BASE_DIR + os.path.sep + dir_name
    os.chdir(path)
    expected_fn = dir_name + ".cbp"
    for file in glob.glob("*.cbp"):
        fn = path + os.path.sep + expected_fn
        if expected_fn != file:
            print('rename: ' + file + ' => ' + file)
            os.rename(path + os.path.sep + file, fn)
        replace(fn, '<Option title="\S+"\s/>', '<Option title="' + dir_name + '" />')
        replace(fn, 'output="bin/Debug/\S+"', 'output="bin/Debug/' + dir_name + '"')
        replace(fn, 'output="bin/Release/\S+"', 'output="bin/Release/' + dir_name + '"')


# Берём все подкаталоги
for d in sd:
    print(d)
    process_dir(d)
