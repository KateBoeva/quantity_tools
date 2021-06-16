import re

from cor_quantity.models.course_elements.CourseElement import CourseElement
from cor_quantity.parsers.CourseParser import CourseParser
from core.const import RAW_COR


class TestElement(CourseElement):
    def __init__(self, filename, count=1):
        self.filename = filename
        super().__init__(count)

    def read(self):
        quiz = CourseParser.parse_raw_file(RAW_COR + self.filename)
        q = CourseParser.parse_raw_file(RAW_COR + "questions.xml")

        ids = []

        for element in quiz.getElementsByTagName("questionid"):
            ids += [child.nodeValue for child in element.childNodes]

        questions = CourseParser.get_tags_data("question", q, ["id"])
        text = []
        for q in questions:
            if q["id"] in ids:
                text += [re.sub('<[^<]+?>', '', q["questiontext"])]

        return " ".join(text)
