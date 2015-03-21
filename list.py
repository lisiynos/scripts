# -*- coding: utf-8 -*-
import os
import re
import sys
import unittest
from random import randrange
from string import Template

# Пишем лог файл по всем действиям
# Если лог не нужен => поставьте False
LOG = False  # True
if LOG:
    sys.stdout = open("list.log", "w", encoding='utf-8')

# Сколько баллов за задачу
BALLS = 100

# По-умолчанию начинаем с текущего каталога
os.chdir(".")
# Но можно выполнить для любого каталога
# os.chdir("D:/denis/testsys/150321_ln/problems")


def subdirs():  # Подкаталоги каталога problems
    return [name for name in os.listdir(".") if os.path.isdir(name)]


# Запись файла: t - шаблон, d - словарь значений, fn - имя файла
def GenFile(t, d, fn, overwrite=False):
    if not overwrite and os.path.isfile(fn):
        return
    print('Gen "%s"' % fn)
    f = open(fn, 'w')
    f.write(Template(t).safe_substitute(d))
    f.close()


# Шаблон файла task.cfg
task_cfg = """InputFile := $TaskID.in;
OutputFile := $TaskID.out;
CheckResult := true;
"""

# solution = ReadTemplate("solution.dpr")
# problem = ReadTemplate("problem.tex")

# contest_id = os.path.split(os.path.split(os.path.dirname( __file__ ))[0])[1]
# contest_name = open("name.txt").read().decode("utf-8") # Название контеста
# print contest_id,'-',contest_name


def filter_tasks(tasks):
    """ Фильтруем id задач """
    tasks = [x.strip() for x in tasks]
    return [x for x in tasks if len(x) > 0 and not x.startswith(".")]


# Порядок задач
orderFile = "order.txt"
tasks = []
if os.path.isfile(orderFile):
    tasks = filter_tasks(open(orderFile).readlines())

if len(tasks) == 0:
    print("Create \"" + orderFile + "\"")
    tasks = filter_tasks(subdirs())
    if len(tasks) == 0:
        print("Tasks not found!")
        exit(0)
    orderF = open(orderFile, 'w')
    for task in filter_tasks(tasks):
        orderF.write("%s\n" % task)
    orderF.close()

if len(tasks) == 0:
    print("Tasks not found!")
    exit(0)


class Task:
    """ Данные о задаче """
    # id - Имя входного/выходного файла задачи
    pass


# Пробегаем все задачи
l = []
test_dir = 'tests'


def parse_statement(s):
    """
    Разбор tex-условия задачи
    :param s: текст условия
    :return: (название_задачи, входной_файл, выходной_файл, time_limit, memory_limit)
    """
    return re.findall(
        r'\\begin\{problem\}\s*\{([^\}]*)\}\s*\{([^\}]*)\}\s*\{([^\}]*)\}\s*\{(\d*)[^\}]*\}\s*\{(\d*)[^\}]*\}',
        s, re.U)


for TaskID in tasks:
    if TaskID == '.idea': continue
    if TaskID == '': continue
    assert len(TaskID) > 0

    # Новый объект - задача
    t = Task()
    t.id = TaskID

    # Генерация task.cfg
    d = {'TaskID': TaskID}
    GenFile(task_cfg, d, "%s/task.cfg" % TaskID, True)
    tests_path = "%s/tests" % TaskID
    if os.path.isfile(tests_path):
        GenFile(task_cfg, d, tests_path + "/task.cfg", True)

    # Вычисляем количество тестов и макрос
    test_count = 0
    t.macros = 'problAIOI'
    while True:
        test_count += 1
        d = {
            TaskID + '/' + test_dir + "/%02d" % test_count: 'problAIOI',
            TaskID + "/%02d" % test_count: 'problIOI',
            TaskID + '/' + test_dir + "/%03d" % test_count: 'problA3IOI',
        }
        find = False
        for filename in d:
            if os.path.isfile(filename):
                t.macros = d[filename]
                find = True
                break

        if not find:
            test_count -= 1
            break

    print("%s - %d" % (TaskID, test_count))
    if test_count == 0:
        continue
    assert test_count > 0

    # Java checker
    javaCheckerFile = "%s/Check.java" % (TaskID)
    if os.path.isfile(javaCheckerFile):
        macros = 'problJIOI'

    # GenFile(solution,d,"%s/solution.dpr" % TaskID)
    # Если нет заготовки .tex файла, создаём её
    for tex_file in ["%s/%s.tex" % (TaskID, TaskID),
                     "%s/statement/%s.ru.tex" % (TaskID, TaskID),
                     "%s/statement/%s.tex" % (TaskID, TaskID),
                     "%s/statements/russian/problem.tex" % (TaskID)]:
        if os.path.isfile(tex_file):
            break
    print(tex_file)

    assert os.path.isfile(tex_file)

    # GenFile(problem,d,tex_file)
    # Читаем заголовок tex файла
    tex_cont = open(tex_file, 'r', encoding='utf-8').read()
    # x = re.findall(r'\\(?P<command>\w+)\{(?P<argA>.*?)\}\{(?P<argB>.*?)\}?\r?\n\{(?P<argC>.*?)\}.*' , tex_cont, re.U)
    x = parse_statement(tex_cont)
    if x:
        first = x[0]
        t.name = first[0]
    else:
        t.name = '!!!'

    if test_count == 0:
        print('NO TESTS!!! ' + TaskID)

    t.preliminary = 1
    preliminaryFile = "%s/preliminary.txt" % TaskID
    try:
        preliminaryF = open(preliminaryFile, 'r')
        t.preliminary = int(preliminaryF.readline().rstrip().lstrip())
        preliminaryF.close()
    except:
        preliminaryF = open(preliminaryFile, 'w')
        preliminaryF.write("%s" % t.preliminary)
        preliminaryF.close()

    balls = [0]
    ballsFile = "%s/balls.txt" % TaskID
    try:
        ballsF = open(ballsFile, 'r')
        bs = ballsF.readline()
        balls = list(map(int, bs.strip().split()))
        ballsF.close()
    except:
        print("File: " + ballsFile)

    print("%s - %d " % (balls, len(balls)))
    if sum(balls) != BALLS or len(balls) != test_count:
        # Количество баллов за все тесты в этой конкретной задаче
        PBalls = BALLS
        # Генерация баллов
        realTests = (test_count - t.preliminary)
        while realTests > PBalls:
            PBalls += BALLS
        balls = [1] * realTests
        while sum(balls) < PBalls:
            balls[randrange(0, realTests, 1)] += 1
        balls = sorted(balls)
        assert sum(balls) == PBalls

        # Добавляем тесты из условия
        balls = [0] * t.preliminary + balls

        # Баллы в строку
        t.balls = " ".join(str(x) for x in balls)

        print('Generate balls: ' + t.balls)
        ballsF = open(ballsFile, 'w', encoding='cp866')
        ballsF.write(t.balls)
        ballsF.close()

    # Баллы в строку
    t.balls = " ".join(str(x) for x in balls)

    l.append(t)

# Генерируем включение условий задач в .tex файл условия
str = ""
problems = "problems = [\n"
problems_acm = "problems = [\n"
Letter = ord('A')
for t in l:
    str += '\prob{%s}\n' % (t.id)
    # ACM
    problems_acm += '\tproblAD (%s, "%s", %s)\n' % (chr(Letter), t.name, t.id)
    problems += '\t %s (%s, "%s", "%s", "%s", "%s")\n' % \
                (t.macros, chr(Letter), t.name, t.id, t.balls, t.preliminary)
    Letter += 1
problems += "];"
problems_acm += "];"


f = open('problems.cfg', 'w', encoding='cp866')
f.write(problems)
f.close()

f = open('acm.cfg', 'w', encoding='cp866')
f.write(problems_acm)
f.close()

f = open('problems.tex.inc', 'w', encoding='utf8')
f.write(str)
f.close()


# Генерируем tex файл условий задач
# st = ReadTemplate("statements.tex")
# st = st.replace('%problem_list%',str)
# st = st.replace('%contest_name%',unicode('').encode("utf-8"))
# f = open('140322_ln'+'.tex', 'w')
# f.write(st)
# f.close()

# Генерируем конфигурационный файл
# st = ReadTemplate("contest.cfg")
# st = st.replace('%problem_list%',unicode(problems).encode('cp866'))
# st = st.replace('%contest_name%',unicode(contest_name).encode('cp866'))
# f = open('..\\'+contest_id+'.cfg', 'w')
# f.write(st)
# f.close()

class Tests(unittest.TestCase):
    """ Модульные тесты для функций и классов """

    def test_parse_problem_text(self):
        self.assertEquals([('Сообщение об ошибке', 'errmess.in', 'errmess.out', '2', '256')],
                          parse_statement("""\\begin{problem}{Сообщение об ошибке}{errmess.in}{errmess.out}
{2 секунды}{256 мебибайт}{}
"""))
        self.assertEquals([('Сообщение об ошибке', 'errmess2.in', 'errmess2.out', '2', '128')],
                          parse_statement("""\\\gdef\\thisproblemauthor{Иван Казменко}
\\gdef\\thisproblemdeveloper{Иван Казменко}
\\begin{problem}{Сообщение об ошибке}
{errmess2.in}   {errmess2.out}
{2 секунды}  {128 мебибайт}{}
"""))
