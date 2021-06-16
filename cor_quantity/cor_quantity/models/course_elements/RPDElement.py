import re

import pdfplumber

from cor_quantity.models.course_elements.CourseElement import CourseElement
from cor_quantity.pattern import Pattern


class RPDElement(CourseElement):
    def __init__(self, filename=None, count=1):
        if filename:
            self.filename = filename
            self.subjects = self.read()
        super().__init__(count)

    def read(self):
        text = ''
        with pdfplumber.open(self.filename) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

        structure_header = "4.2 Содержание дисциплины"
        next_header = "4.3 Структура и содержание самостоятельной работы дисциплины (модуля)"

        course_structure = text[text.find(structure_header) + len(structure_header):text.find(next_header)]
        subjects = [m.start() for m in re.finditer(Pattern.RPD_THEME_HEADER, course_structure)]

        blocks = []

        for key, value in enumerate(subjects):
            next_key = key + 1
            theme = course_structure[value:subjects[next_key]] if next_key < len(subjects) else course_structure[value:]
            new = re.sub(Pattern.RPD_THEME, "", theme).replace(".\n", "").replace("\n", "")
            time = re.findall(Pattern.NUMBER, re.search(Pattern.TIME, theme).group())[0]
            content = theme[theme.find("):"):]
            blocks.append({
                'subject': new,
                'time': time,
                'content': content
            })

        return blocks

    def get_not_existed_subjects(self, course_subjects):
        tmp = []
        cst = []

        for item in course_subjects:
            cst.append(self.preprocess(item))

        for subject in self.subjects:
            subject_tokens = self.preprocess(subject['subject'])

            not_in_rpd = True
            for key, item in enumerate(cst):
                if len(subject_tokens) == len(item) and len(list(set(subject_tokens) & set(item))) == len(item):
                    not_in_rpd = False

            if not_in_rpd:
                tmp.append(subject['subject'])

        return tmp

    def get_existed_subjects(self, course_subjects):
        tmp = []
        cst = []

        for item in course_subjects:
            cst.append(self.preprocess(item))

        for subject in self.subjects:
            subject_tokens = self.preprocess(subject['subject'])

            for key, item in enumerate(cst):
                if len(subject_tokens) == len(item) and len(list(set(subject_tokens) & set(item))) == len(item):
                    tmp.append(course_subjects[key])

        return tmp
