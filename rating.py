# -*- coding: utf-8 -*-
from __future__ import print_function

import os

os.chdir(".")


# os.chdir("C:/testsys/monitors")


def parse_team_name(team_name):
    """ Разбор имени команды на составные части """
    # Удаляем всё что до :
    if team_name.find(":") != -1:
        prefix, team_name = team_name.split(":")
    # Удаляем пробелы в начале и конце, делим по запятым и опять удаляем пробелы
    return [x.strip() for x in team_name.strip().split(",")]


def is_team(team_name):
    return team_name.find(":") != -1


def ignore_team(team_name):
    global team_names
    for w in ["Cheater", u"Я верю", u"ЖЮРИ", u"Жюри",
              u"--== Проверка корректности", u"Снегурочки:", u"Маги:", u"Как угодно:",
              u"Помошники главного землемера:"]:
        if team_name.find(w) != -1:
            # print "Ignore: ", team_name
            return True
    if (team_name.find(":") != -1) or (team_name in [u'Угаров Антон, Николаев Дмитрий',
                                                     u'Привалихин Алексей, Пирогов Михаил']):  # or t.name.find(",") != -1
        # print "#$ ",t.name, u"- старшая"
        return True
    return False


def uts(team_name):
    """ Участники УТС - * в имени """
    return team_name.find('*') != -1


def teams_o(team_name):
    """ Старшая группа - есть # """
    if ignore_team(team_name):
        return False
    return team_name.find('#') != -1


def teams_y(team_name):
    """ Младшая группа - нет # """
    if ignore_team(team_name):
        return False
    return not teams_o(team_name)


class Team:
    """ Команда """

    def __init__(self):
        self.id = 0  # id команды
        self.name = ""
        self.solved = set()  # Решённые задачи
        self.time = 0  # Штрафных минут
        self.task_score = {}

    # Сумма баллов за все задачи
    def score(self):
        return sum(self.task_score.values())

    def score_day(self, day):
        return sum(self.task_score[task] for task in self.task_score.keys() if task.startswith(day + "#"))

    def submit(self, task_id, attempt, time, result, test=0):
        """ Отправка решения """
        # Анализируем результат (важны только успешные сдачи)
        if result == "OK":
            # Если задача уже была решена, то игнорируем попытку
            if task_id in self.solved: return
            # Время в минутах
            minutes = (int(time) + 25) // 60
            # Задача удачно сдана
            self.time += minutes + (int(attempt) - 1) * 20  # добавляем в штрафное время текущее время
            self.solved.add(task_id)  # а задачу в список решённых
            self.task_score[task_id] = 100  # Ставим 100 баллов за полностью решённую задачу
        if isinstance(result, int):
            # Записываем результат для этой задачи
            if result > 0:
                self.task_score[task_id] = result
                self.solved.add(task_id)  # ..задачу в список решённых
                # if self.id == 24:
                # print("        team.submit('%s',%s,%s,'%s')" % (task_id, attempt, time, result))
                # print("        self.assertEqual(%s, len(team.solved))" % len(self.solved))
                # print("        self.assertEqual(%s, team.time)" % self.time)

    def __str__(self):
        """ В виде строки """
        return "%s %d %d" % (self.name, len(self.solved), self.time)


class Contest:
    pass


class Problem:
    """ Задача """
    pass


# Команды
teams = {}


def ParseMonitor(filename):
    global teams
    print('*** Parse: "%s" ***' % filename)
    # Открываем лог контеста на чтение и читаем его целиком в строку
    f = open(filename, "rb")
    text = f.read()
    f.close()
    # Разделяем текст по символу EOF (1A) и раскодируем из кодировки Windows-1251
    EOF_index = text.find(b'\x1a')
    data = text[EOF_index + 1:].decode('cp1251')
    # Контест
    c = Contest()
    # Делим на строки по переносам строки
    lines = data.split('\x0d\x0a')
    for file_line in lines:
        # Игнорируем пустые строки
        if not len(file_line): continue
        # Отделяем команду и агрументы
        cmd, arg = parse_cmd(file_line)
        # For unit-tests generating
        # print "self.assertEqual(%s, parse_cmd('%s'))" % ((cmd, arg), file_line)

        if cmd == "@contest":  # Название контеста
            c.ContestName = arg
        elif cmd == "@startat":  # Начало контеста
            c.StartAt = arg
        elif cmd == "@contlen":  # Длина контеста в минутах
            c.ContLen = arg
        elif cmd == "@now":  # Секунда сейчас
            c.Now = arg
        elif cmd == "@state":  # Состояние соревнования
            c.State = arg
        elif cmd == "@freeze":
            c.Freeze = arg
        elif cmd == "@problems":  # Количество задач
            c.Problems = arg
        elif cmd == "@teams":  # Количество команд
            c.Teams = arg
        elif cmd == "@submissions":  # Количество посылок (сабмитов)
            c.Submissions = arg
        elif cmd == "@p":  # Данные о задачах нам пока не нужны (достаточно только их id)
            # print s,s.find('"')
            # if arg.find('"') >= 0:
            # l = s.split('"')[1::2]  # the [1::2] is a slicing which extracts odd values
            # name = l[0]  # Берём только самый первый элемент
            # id, name1, points, unknown = s.replace(name, '#').split(
            # ',')  # Извлечённую строку заменяем на '#' и игнорируем её при разборе
            # else:
            id, name, points, unknown = arg
            # print id, name, points, unknown
        elif cmd == "@t":
            # @t 11,0,1,Иванов Иван Иванович
            t = Team()
            t.id, t.u0, t.u1, t.name = arg
            if not t.id in teams:
                teams[t.id] = t  # Добавляем команду в словарь
            else:  # Обновляем название
                teams[t.id].name = t.name
                # print u"Команда "+t.id+u" уже занесена"
        elif cmd == "@s":  # @s 14,A6,3,427038,ML,35
            if len(arg) == 5:
                team_id, task_id, no, second, result = arg
                teams[team_id].submit(filename + "#" + str(task_id), no, second, result)
            elif len(arg) == 6:
                team_id, task_id, no, second, result, test = arg
                teams[team_id].submit(filename + "#" + str(task_id), no, second, result, test)
            else:
                raise Exception("Unknown format: %line" % arg)
        else:
            print('Unknown command "%s" arg = %s' % (cmd, arg))
    return c


# Сортировка участников по результатам
def TeamCmpFunc(c1, c2):
    if len(c1.solved) < len(c2.solved): return 1
    if len(c1.solved) > len(c2.solved): return -1
    if c1.time > c2.time: return 1
    if c1.time < c2.time: return -1
    return 0


def IOICmpFunc(c1, c2):
    if c1.score() < c2.score(): return 1
    if c1.score() > c2.score(): return -1
    return 0


def parse_team_str(team_str):
    """ Выделяем из строки id команды """
    s = re.findall(r'\s+team\w\s+\((\d+),\s".+\)', team_str)
    if len(s) > 0:
        return s[0]
    else:
        return None


# Разбираем файлы групп
def Parse(FileName):
    teams = []
    # Открываем лог контеста на чтение и читаем его целиком в строку
    for s in open(FileName, "r", encoding='cp866'):
        team_id = parse_team_str(s)
        if team_id:
            teams.append(team_id)
    return teams


# Модульные тесты для функций использующихся при генерации рейтинга

# Автоматические тесты
import unittest


# Пробуем разобрать значение как число
def try_parse(value):
    # Убираем начальные и концевые разделители
    value = value.strip()
    try:
        return int(value)  # Целое число?
    except ValueError:
        try:
            return float(value)  # Действительное число?
        except ValueError:
            # Это строка в кавычках? Убираем кавычки из строчки
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value


import re


def parse_cmd(line):
    """ Разбор команды """
    # Отделяем команду (она отделена пробелом)
    s = line.split()
    cmd = s[0]  # и её аргументы (если есть)
    assert cmd[0] == '@'  # Все команды начинаются с @
    arg_line = line[len(cmd):].strip()

    # Разделение строки по запятым на аргументы (учитывая двойные кавычки)
    arg = re.findall(r'([^,"]+|"[^"]*")(?=,|$)', arg_line)

    # Преобразуем что можем в числа (целые и действительные)
    arg = tuple(try_parse(x) for x in arg)
    # Если аргумент всего один, то его и возвращаем
    if len(arg) == 1:
        return cmd, arg[0]
    return cmd, arg


from os import listdir, getcwd


def get_monitor_files(session_id):
    """ Получить файлы мониторов для заданной сессии """
    files = []
    for i in listdir(getcwd()):
        if i.startswith('jm' + session_id):
            files.append(i)
    return files


class Reporter:
    def __init__(self, IOIMode, files):
        self.IOIMode = IOIMode
        self.files = files

    def dates(self):
        d = []
        for filename in self.files:
            # Получаем дату по имени файла, если такая дата уже есть, то пропускаем
            date = filename_to_date(filename)
            # if d.count(date) == 0:  # Если такой даты ещё нет
            d.append(date)
        return d

    def column_headers(self):
        if self.IOIMode:
            return ['№', 'Фамилия Имя Отчество'] + self.dates() + ['Всего баллов']
        else:
            return '№', 'Фамилия Имя Отчество', 'Решено задач', 'Штрафное время'

    def table_header(self, files):
        # th = "".join(["<th>%s</th>" % x for x in self.column_headers(files)])
        th = "".join(["<th>%s</th>" % x for x in self.column_headers()])
        return "<thead><tr>%s</tr></thead>\n" % th

    def row(self, row):
        th = "".join(["<td>%s</td>" % x for x in row])
        return "<tr>%s</tr>\n" % th


def filename_to_date(filename):
    return filename[6:8] + "." + filename[4:6]


class TestRating(unittest.TestCase):
    """ Модульные тесты для функций и классов используемых при генерации рейтинга """

    def test_parse_team_name(self):
        """ Разделение команды на участников """
        self.assertEqual(['One1', 'Two', 'Three'], parse_team_name("One1, Two, Three"))
        self.assertEqual(['One1', 'Two', 'Three'], parse_team_name("Team: One1, Two, Three"))
        self.assertEqual(['Константин Шандуренко', 'Михаил Пирогов', 'Батраков Александр'],
                         parse_team_name("Команда: Константин Шандуренко, Михаил Пирогов, Батраков Александр "))

    def test_parse_cmd(self):
        """ Разбор команд """
        self.assertEqual(('@contest', "Лисий Нос, дистанционная сессия, июнь 2014 года"),
                         parse_cmd('@contest "Лисий Нос, дистанционная сессия, июнь 2014 года"'))
        self.assertEqual(('@startat', '17.07.2014 11:56:59'), parse_cmd('@startat 17.07.2014 11:56:59'))
        self.assertEqual(('@contlen', 100500), parse_cmd('@contlen 100500'))
        self.assertEqual(('@now', 1571182), parse_cmd('@now 1571182'))
        self.assertEqual(('@state', 'RUNNING'), parse_cmd('@state RUNNING'))
        self.assertEqual(('@freeze', 100500), parse_cmd('@freeze 100500'))
        self.assertEqual(('@problems', 26), parse_cmd('@problems 26'))
        self.assertEqual(('@teams', 31), parse_cmd('@teams 31'))
        self.assertEqual(('@state', 'OVER'), parse_cmd('@state OVER'))
        self.assertEqual(('@p', ("A", "Соревнование картингистов", 20, 0)),
                         parse_cmd('@p A,Соревнование картингистов,20,0'))
        self.assertEqual(('@t', (14, 0, 1, "Пасечник Любовь Ивановна (Выборг, СОШ №7, 10)")),
                         parse_cmd('@t 14,0,1,"Пасечник Любовь Ивановна (Выборг, СОШ №7, 10)"'))
        self.assertEqual(('@t', ("XX", "YY", 1, "Пасечник Любовь Ивановна (Выборг, СОШ №7, 10)")),
                         parse_cmd('@t XX,"YY",1,"Пасечник Любовь Ивановна (Выборг, СОШ №7, 10)"'))
        self.assertEqual(('@p', ('O', 'LEGO', 20, 0)), parse_cmd('@p O,LEGO,20,0'))
        self.assertEqual(('@s', ('J6', 'A', 1, 505, '--', 11)), parse_cmd('@s J6,A,1,505,--,11'))
        self.assertEqual(('@s', ('J6', 'A', 1, 505, '--', 11)), parse_cmd('@s  J6 , A , 1 , 505 , -- , 11  '))

    def test_ACM(self):
        team = Team()
        team.submit('A', 1, 260987, 'OK')
        self.assertEqual(1, len(team.solved))
        self.assertEqual(4350, team.time)
        team.submit('P', 1, 295819, 'WA')
        self.assertEqual(1, len(team.solved))
        self.assertEqual(4350, team.time)
        team.submit('P', 2, 299330, 'WA')
        self.assertEqual(1, len(team.solved))
        self.assertEqual(4350, team.time)
        team.submit('B', 1, 383935, 'OK')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(10749, team.time)
        # После успешной отправки последующие игнорируются
        team.submit('B', 1, 384935, 'WA')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(10749, team.time)
        team.submit('C', 1, 385629, 'OK')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(17176, team.time)
        team.submit('D', 1, 451188, 'OK')
        self.assertEqual(4, len(team.solved))
        self.assertEqual(24696, team.time)
        team.submit('M', 1, 453503, 'OK')
        self.assertEqual(5, len(team.solved))
        self.assertEqual(32254, team.time)

    def test_acm2(self):
        """ Regression test for ACM """
        team = Team()
        team.submit('jm140721_ln.dat#B', 1, 33789, 'OK')
        self.assertEqual(1, len(team.solved))
        self.assertEqual(563, team.time)
        self.assertEqual(100, team.score())
        team.submit('jm140721_ln.dat#A', 1, 39547, 'OK')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(1222, team.time)
        self.assertEqual(200, team.score())
        team.submit('jm140721_ln.dat#E', 1, 43191, 'TL')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(1222, team.time)
        self.assertEqual(200, team.score())
        team.submit('jm140721_ln.dat#E', 2, 43412, 'TL')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(1222, team.time)
        self.assertEqual(200, team.score())
        team.submit('jm140721_ln.dat#E', 3, 43921, 'TL')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(1222, team.time)
        self.assertEqual(200, team.score())
        team.submit('jm140721_ln.dat#E', 4, 44488, 'TL')
        self.assertEqual(2, len(team.solved))
        self.assertEqual(1222, team.time)
        team.submit('jm140721_ln.dat#H', 1, 47514, 'OK')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)
        self.assertEqual(300, team.score())
        team.submit('jm140721_ln.dat#I', 1, 51104, 'RT')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)
        team.submit('jm140721_ln.dat#I', 2, 51148, 'RT')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)
        team.submit('jm140721_ln.dat#I', 3, 51959, 'RT')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)
        team.submit('jm140721_ln.dat#I', 4, 72829, 'RT')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)
        team.submit('jm140721_ln.dat#I', 5, 72979, 'RT')
        self.assertEqual(3, len(team.solved))
        self.assertEqual(2014, team.time)

    def test_IOI(self):
        """ Работа в IOI-режиме """
        team = Team()
        self.assertEqual(0, team.score())
        self.assertEqual(0, len(team.solved))
        team.submit('C', 1, 43261, 100)
        self.assertEqual(100, team.score())
        self.assertEqual(1, len(team.solved))
        # Следующая попытка хуже :)
        team.submit('C', 1, 43261, 98)
        self.assertEqual(98, team.score())
        self.assertEqual(1, len(team.solved))
        team.submit('D', 1, 43261, 200)
        self.assertEqual(298, team.score())
        self.assertEqual(2, len(team.solved))

    def test_ignore_team(self):
        """ Кто не должен войти в рейтинг """
        self.assertTrue(ignore_team(u"Жюри:"))
        self.assertTrue(ignore_team(u"Жюри: Иван Иванович"))
        self.assertTrue(ignore_team(u"Жюри: Сергей Петрович"))
        self.assertTrue(ignore_team(u"Cheater"))
        self.assertTrue(ignore_team(u"Я верю"))
        self.assertTrue(ignore_team(u"Я верю что вы"))
        self.assertTrue(ignore_team(u"Я верю :)"))
        # Нормальные названия команд
        self.assertFalse(ignore_team(u"Мамаев Даниил #"))

    def test_reporter(self):
        report = Reporter(False, [])
        self.assertEqual(('№', 'Фамилия Имя Отчество', 'Решено задач', 'Штрафное время'), report.column_headers())

    def test_filename_to_date(self):
        self.assertEqual("22.07", filename_to_date("jm140722_ln.dat"))

    def test_parse_teams(self):
        self.assertEqual('53', parse_team_str(
            '  teamX (53, "Иванов Иван Иванович", "pass")'))
        teams = Parse('data/teams_y.cfg')
        self.assertEqual(['31', '38', '40'],
                         sorted(teams))


if __name__ == '__main__':
    unittest.main()
