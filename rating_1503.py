# -*- coding: utf-8 -*-
import sys
import functools
from os.path import isdir

from rating import *


TITLE = """Рейтинг по учебно-тренировочным сборам по информатике 2015 года (16-21 марта)"""

LOG = False
if LOG:
    sys.stdout = open("rating_1503.txt", "w", encoding='utf8')

# За какие сессии собирать рейтинг
session = '1503'  # ['1210','1211'] # Два месяца сразу
print('Собираем рейтинг за: %s' % session)

# Генерация выходного файла
TexFileName = "rating_" + session + ".tex"
tex = open(TexFileName, "w")
tex.write("\\documentclass[20pt]{article}\n")
tex.write("\\usepackage[T2A]{fontenc}\n")
tex.write("\\usepackage[utf8]{inputenc}\n")
tex.write("\\usepackage[english,russian]{babel}\n")
tex.write("\\usepackage{amsmath}\n")
tex.write("\\usepackage{amssymb}\n")
tex.write("\\usepackage{amsfonts}\n")
tex.write("\\usepackage{amsthm}\n")
tex.write("\\renewcommand{\\t}{\\texttt}\n")
tex.write("\\pagestyle{empty}\n")
tex.write("\\oddsidemargin -1.0cm\n")
tex.write("\\evensidemargin 0.0in\n")
tex.write("\\headheight 0.0in\n")
tex.write("\\topmargin 0.0in\n")
tex.write("\\leftmargin -1.0cm\n")
tex.write("\\textwidth=17cm\n")
tex.write("\\textheight=24cm\n")
tex.write("\\begin{document}\n")


def gen_table(tex):
    global teams
    tex.write("\\begin{tabular}{ | c | c | c | }\n")
    tex.write("  \\hline\n")
    count = 0
    for t in teams:
        if t.name.find("Cheater") != -1 or t.name.find("Я верю") != -1: continue
        count += 1
        name_utf = t.name  # .encode("utf-8")
        solved = "%d" % len(t.solved)
        time = "%d" % t.time
        tex.write("  " + ("%d" % count) + " & " + name_utf + " & " + solved + " (" + time + ") \\\\ \\hline \n")
    tex.write("\\end{tabular}\n")


files = get_monitor_files(session)
print('Собираем информацию из файлов: %s' % files)
# Исключаем файлы других сессий/дистанционки и т.д.
for exclude in ['jm150309_ln.dat', 'jm150310_ln.dat']:
    files.remove(exclude)

# Разбираем все файлы с мониторами
for fileName in files:
    ParseMonitor(fileName)

# Словарь для поиска участников по имени
teamByName = {}
for t in teams:
    team_name = teams[t].name
    assert team_name == team_name.strip()
    assert len(team_name) > 0
    teamByName[team_name] = t
print('Команды по имени')
print('----------------')
for key, value in teamByName.items():
    print("%s => %s" % (key, value))

# Локальный файл
HTMLFileName = session + ".html"

# Если есть nginx, то файл в nginx
nginx_path = "C:\\nginx\\nginx-1.5.2\\html"
if isdir(nginx_path):
    HTMLFileName = nginx_path + "\\" + session + ".html"

print(HTMLFileName)
h = open(HTMLFileName, "w", encoding='utf8')
# Печать заголовка всего файла
h.write("""<html lang="ru" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>""" + TITLE + """</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
</head>
<body>""")

IOIMode = True
report = Reporter(IOIMode, files)

h.write("""<h2>%s</h2>\n""" % TITLE)

print('Разделяем команды на участников и добавляем задачи к участникам')
print('---------------------------------------------------------------')
for t in teams:
    team = teams[t]
    if team.name.find(u"Жюри:") != -1:
        continue
    if team.name.find(":") != -1:  # or team.name.find(",") != -1
        teamName = team.name
        print("Команда: \"%s\", делим на участников:" % teamName)
        users = parse_team_name(teamName)
        for userName in users:
            userNameNormalized = userName.strip().replace(u'ё', u'е')
            print("Участник команды: \"%s\"" % userNameNormalized)
            if not userNameNormalized in teamByName:
                print("Участник команды не найден в обшем списке: \"%s\" " % userNameNormalized)
                continue
            teamID = teamByName[userNameNormalized]
            teams[teamID].solved.union(team.solved)  # Обьединяем решённые задачи
            teams[teamID].time += team.time

teams = list(teams.values())  # Преобразуем словарь в список
# Сортируем рейтинг
teams = sorted(teams, key=functools.cmp_to_key(IOICmpFunc if report.IOIMode else TeamCmpFunc))

print()
print('Все участники')
print('-------------')
for team in teams:
    print(team.name)
print()


def write_teams(name, teams):
    """ Генерация таблицы """
    # Если таких команд нет, то нечего и в рейтинг писать
    if len(teams) == 0:
        return
    h.write("<h3>%s</h3>\n<table border=1>\n%s\n" % (name, report.table_header(files)))
    count = 0
    for t in teams:
        count += 1
        name_utf = t.name.replace('#', '').strip()
        solved = len(t.solved)
        if int(solved) == 0:
            print(' ' + name_utf + ' - Пропускаем тех, у кого 0 решённых задач')
            continue
        if IOIMode:
            h.write(report.row([count, name_utf] + [t.score_day(d) for d in report.files] + [t.score()]))
        else:
            h.write(report.row([count, name_utf, solved, t.time]))
    h.write("</table>\n")


# Обычная сессия (не УТС)
write_teams("Младшая группа", [t for t in teams if teams_y(t.name)])
write_teams("Старшая группа", [t for t in teams if teams_o(t.name)])

uts_y = [t for t in teams if teams_y(t.name) and uts(t.name)]
uts_o = [t for t in teams if teams_o(t.name) and uts(t.name)]

# Если есть участники УТС, то есть ещё и часть про УТС
if len(uts_o) > 0 or len(uts_y) > 0:
    h.write("""\n<h2>Учебно-тренировочные сборы по информатике</h2>\n""")
    write_teams("Младшая группа", uts_y)
    write_teams("Старшая группа", uts_o)

import datetime

now_time = datetime.datetime.now()
h.write("Рейтинг собран: " + now_time.strftime("%d.%m.%Y %I:%M:%S"))  # форматируем дату

# Конец HTML-файла
h.write("""
  </body></html>""")
h.close()

tex.write("\n")

gen_table(tex)
tex.write("\n\n\\vspace{30 mm}\n\n")

tex.write("\\end{document}\n")

tex.close()
# Создаём итоговый PDF файл
# call("pdflatex "+TexFileName)