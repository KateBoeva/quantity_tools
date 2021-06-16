from cor_quantity.models.course_elements.CourseElement import CourseElement


class PresentationElement(CourseElement):
    def __init__(self, min_slides, max_slides, count, presentation=None):
        self.min_slides = min_slides
        self.max_slides = max_slides
        if presentation:
            self.presentation = presentation
        super().__init__(count)

    def read(self):
        text_runs = ''

        if self.presentation:
            for slide in self.presentation.slides:
                for shape in slide.shapes:
                    if not shape.has_text_frame:
                        continue
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            text_runs += run.text

        return self.preprocess(text_runs)

    def get_slides_count(self):
        if self.presentation:
            return len(self.presentation.slides)

        return 0
