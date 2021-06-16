from enum import Enum


class ActivityType(Enum):
    RPD = 'rpd'
    VIDEO = 'video'
    PRESENTATION = 'presentation'
    TEXT = 'text'
    LECTURE = 'lecture'
    TEST = 'test'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @staticmethod
    def get_normalized_stop_words():
        return {
            ActivityType.RPD: ['рабочая программа дисциплины', 'рпд', 'тематический план дисциплины'],
            ActivityType.TEXT: [],
            ActivityType.LECTURE: ['лекция'],
            ActivityType.PRESENTATION: ['презентация', 'слайд'],
            ActivityType.VIDEO: ['видео', 'промовидео', 'ролик'],
            ActivityType.TEST: ['тест', 'контроль знаний'],
        }

    @staticmethod
    def get_stop_words(item):
        return ActivityType.get_normalized_stop_words()[item]

    @staticmethod
    def check_type(row, a_type):
        for key in ActivityType.get_normalized_stop_words()[a_type]:
            if key.find(row.lower()) > 0:
                return True

        return False

    def define_element_types(self, row):
        content = ' '.join(row).lower()
        types = []

        for a_type in self.list():
            if self.check_type(content, a_type):
                types.append(a_type)

        return [a_type for a_type in self.list() if self.check_type(content, a_type)]

