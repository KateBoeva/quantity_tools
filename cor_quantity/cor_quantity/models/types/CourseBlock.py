from cor_quantity.models.types.CourseBlockType import CourseBlockType


class CourseBlock:
    def __init__(self, block_type, title):
        self.block_type = block_type
        self.title = title

    def get_stopwords(self):
        return CourseBlockType.get_block_type_stopwords(self.block_type)
