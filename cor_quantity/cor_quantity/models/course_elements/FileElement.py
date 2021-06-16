import pdfplumber

from cor_quantity.models.course_elements.CourseElement import CourseElement


class FileElement(CourseElement):
    def __init__(self, filename, count=1):
        self.filename = filename
        super().__init__(count)

    def read(self):
        content = ""
        with pdfplumber.open(self.filename) as pdf:
            for page in pdf.pages:
                content += page.extract_text()

            pdf.close()
            return self.preprocess(content)
