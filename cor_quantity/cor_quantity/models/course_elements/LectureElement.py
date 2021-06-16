from cor_quantity.models.course_elements.CourseElement import CourseElement


class LectureElement(CourseElement):
    def __init__(self, title=None, content=None, count=1):
        if title:
            self.title = title
        if content:
            self.content = content
        super().__init__(count)

    def read(self):
        return self.preprocess(self.content)
