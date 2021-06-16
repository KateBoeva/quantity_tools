import re
import tarfile

from fuzzywuzzy import fuzz
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords
from youtube_easy_api.easy_wrapper import *

from core.const import *
from core.messages import *
from config import DEFAULT_SIMILARITY
from cor_quantity.models.course_elements.TestElement import TestElement
from cor_quantity.models.course_elements.PresentationElement import PresentationElement
from cor_quantity.models.course_elements.RPDElement import RPDElement
from cor_quantity.models.course_elements.VideoElement import VideoElement
from cor_quantity.models.types.CourseBlockType import CourseBlockType
from cor_quantity.parsers.CourseParser import CourseParser
from cor_quantity.parsers.OrderParser import OrderParser


def save_file(f, name):
    with open(TMP_DIR + name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def read_order(request):
    """ ЧТЕНИЕ РЕГЛАМЕНТА """
    save_file(request.files['order'], ORDER)
    order = TMP_DIR + ORDER
    parser = OrderParser(order)

    return parser


def read_course(request, is_test=True):
    """ ЧТЕНИЕ MBZ-ФАЙЛА """
    file = request.files['cor']
    file.save(os.path.join(TMP_DIR, ZIPPED_COR_FILE))

    with tarfile.open(TMP_DIR + ZIPPED_COR_FILE, "r:gz") as f:
        f.extractall(RAW_COR)

    path = RAW_COR

    main_file = CourseParser.parse_raw_file(path + 'moodle_backup.xml')
    parser = CourseParser(main_file, path)

    return parser


def are_themes_equal(first, second):
    from cor_quantity.models.course_elements.CourseElement import CourseElement
    first = CourseElement.preprocess(first)
    second = CourseElement.preprocess(second)

    return len(first) == len(second) and len(list(set(first) & set(second))) == len(second)


def analyze(course, order):
    diff = []
    course_subjects = course.get_subjects()
    course = course.parse()
    order = order.parse()
    types = {}
    # dont - к курсу не приложены следующие элементы: ... TODO проверить
    dont = {}
    for block in order:
        types.update({block: []})
        dont.update({block: []})
        for element in order[block]:
            types[block].append(type(element))

    course_types = {}
    for block in course:
        course_types.update({block: []})
        for element in course[block]:
            course_types[block].append(type(element))

    for block in types:
        for element in order[block]:
            if type(element) not in course_types[block]:
                dont[block].append(element)

    is_rpd_exists = True
    for block in dont:
        if RPDElement in dont[block]:
            is_rpd_exists = False

    if not is_rpd_exists:
        return [RPD_NOT_EXISTED]

    if is_rpd_exists:
        for block in course:
            for element in course[block]:
                for item in course[block][element]:
                    if type(item) == RPDElement:
                        not_in_rpd = item.get_not_existed_subjects(course_subjects)

                        if len(not_in_rpd) > 0:
                            diff += [THEMES_NOT_IN_RPD + ", ".join(not_in_rpd) + "."]

                        in_rpd = item.get_existed_subjects(course_subjects)

                        for subject in in_rpd:
                            subject_activities = course[CourseBlockType.SUBJECT][subject]
                            content = []
                            for activity in subject_activities:
                                if type(activity) not in [VideoElement, RPDElement, TestElement]:
                                    content.append(activity.read())

                            not_content = []
                            video_size = []
                            pres_size = []
                            test_content = []
                            for theme in item.subjects:
                                if are_themes_equal(theme['subject'], subject):

                                    similarity = fuzz.token_set_ratio(theme['content'], content)
                                    if similarity < DEFAULT_SIMILARITY:
                                        not_content += [theme['subject']]

                                for activity in course[CourseBlockType.SUBJECT][subject]:
                                    if type(activity) == VideoElement:
                                        if not activity.min_d < activity.duration < activity.max_d:
                                            video_size += [theme['subject']]
                                    elif type(activity) == TestElement:
                                        similarity = fuzz.token_set_ratio(activity.read(), content)
                                        if similarity < DEFAULT_SIMILARITY:
                                            test_content += [theme['subject']]
                                    elif type(activity) == PresentationElement:
                                        if not activity.min_slides < activity.get_slides_count / theme['time'] < activity.max_slides:
                                            pres_size += [theme['subject']]

                            if len(not_content) > 0:
                                diff += [WRONG_CONTENT_THEMES + ", ".join(not_content) + "."]
                            if len(video_size) > 0:
                                diff += [WRONG_VIDEO + ", ".join(video_size) + "."]
                            if len(pres_size) > 0:
                                diff += [WRONG_PRESENTATION + ", ".join(pres_size) + "."]
                            if len(test_content) > 0:
                                diff += [WRONG_TEST + ", ".join(test_content) + "."]

    return "\n".join(diff)


def check(request):
    # чтение файла регламента
    order = read_order(request)
    # чтение файла курса
    course = read_course(request)
    # получение результатов о проверке
    return analyze(course, order)

