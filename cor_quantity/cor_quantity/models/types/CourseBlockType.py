from enum import Enum


class CourseBlockType(Enum):
    INTRO = 'intro'
    SUBJECT = 'subject'
    INTERIM = 'interim'
    CONTROL = 'control'

    @staticmethod
    def get_block_types():
        return [
            CourseBlockType.INTRO,
            CourseBlockType.SUBJECT,
            CourseBlockType.INTERIM,
            CourseBlockType.CONTROL
        ]

    @staticmethod
    def get_blocks_stopwords():
        return {
            CourseBlockType.INTRO: ["введен", "вводн", "общ"],
            CourseBlockType.SUBJECT: ["тем", "модул", "лекц"],
            CourseBlockType.INTERIM: ["промежуточ"],
            CourseBlockType.CONTROL: ["итог"]
        }

    @staticmethod
    def get_block_type_stopwords(block_type):
        return CourseBlockType.get_blocks_stopwords()[block_type]

    @staticmethod
    def get_block_type(block_title):
        def is_module_of_type(title, block_type):
            for word in CourseBlockType.get_block_type_stopwords(block_type):
                if word in title.lower():
                    return True

            return False

        if block_title == CourseBlockType.INTRO.value or block_title == '0' or block_title in CourseBlockType.get_block_type_stopwords(CourseBlockType.INTRO):
            return CourseBlockType.INTRO
        elif is_module_of_type(block_title, CourseBlockType.INTERIM):
            return CourseBlockType.INTERIM
        elif is_module_of_type(block_title, CourseBlockType.CONTROL):
            return CourseBlockType.CONTROL
        else:
            return CourseBlockType.SUBJECT
