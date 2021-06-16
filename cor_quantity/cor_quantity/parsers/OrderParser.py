import re

import pdfplumber

from cor_quantity.models.types.ActivityType import ActivityType
from cor_quantity.models.course_elements.LectureElement import LectureElement
from cor_quantity.models.course_elements.PresentationElement import PresentationElement
from cor_quantity.models.course_elements.RPDElement import RPDElement
from cor_quantity.models.course_elements.TestElement import TestElement
from cor_quantity.models.course_elements.TextElement import TextElement
from cor_quantity.models.course_elements.VideoElement import VideoElement
from cor_quantity.models.types.CourseBlock import CourseBlock
from cor_quantity.models.types.CourseBlockType import CourseBlockType
from cor_quantity.parsers.Parser import Parser
from cor_quantity.pattern import Pattern


class OrderParser(Parser):
    def __init__(self, order_path):
        self.order_path = order_path
        self.blocks = []

    def __get_extreme_point(self, string, synonyms):
        string = string.replace("  ", " ").lower()

        for synonym in synonyms:
            if string.find(synonym) > 0:
                return re.findall(Pattern.NUMBER, string)[0]

        return None

    def __get_max(self, string):
        return self.__get_extreme_point(string, ['максим', 'не более'])

    def __get_min(self, string):
        return self.__get_extreme_point(string, ['миним', 'не менее'])

    def __parse_video(self, item):
        video_count = re.search(Pattern.VIDEO_COUNT, ' '.join(item))
        if video_count:
            video_count = re.findall(Pattern.NUMBER, video_count.group())
            video_count = int(video_count[0]) if len(video_count) > 0 else 1
        else:
            video_count = 1

        extreme = re.search(Pattern.VIDEO_EXTREME, ' '.join(item))
        extreme = extreme.group() if extreme else ''

        min_d = self.__get_min(extreme)
        max_d = self.__get_max(extreme)

        duration = re.search(Pattern.VIDEO_DURATION, ' '.join(item))

        if duration:
            duration = duration.group()
            prepared = re.findall(Pattern.NUMBER, duration)
            min_d = prepared[0]
            max_d = prepared[1] if len(prepared) > 1 else None

        return VideoElement(min_d, max_d, 'order', video_count)

    def __parse_presentation(self, item):
        pres_count = re.findall(Pattern.PRESENTATION_COUNT, ' '.join(item))
        pres_count = pres_count[0] if len(pres_count) > 0 else 1

        slides = re.findall(Pattern.PRES_SLIDES_COUNT, ' '.join(item))[0]
        min_slides = self.__get_min(slides)
        max_slides = self.__get_max(slides)

        return PresentationElement(min_slides, max_slides, pres_count)

    def __parse_test(self, item):
        quiz_count = re.findall(Pattern.NUMBER, ' '.join(item))
        min_quiz = quiz_count[0] if len(quiz_count) > 0 else None
        max_quiz = quiz_count[1] if len(quiz_count) > 1 else None

        return TestElement(min_quiz, max_quiz)

    def __get_course_element(self, element, item):
        if element == ActivityType.RPD:
            return RPDElement()
        elif element == ActivityType.VIDEO:
            return self.__parse_video(item)
        elif element == ActivityType.PRESENTATION:
            return self.__parse_presentation(item)
        elif element == ActivityType.TEXT:
            return TextElement()
        elif element == ActivityType.LECTURE:
            return LectureElement()
        elif element == ActivityType.TEST:
            return self.__parse_test(item)

        return None

    def __define_block_name(self, key):
        blocks = CourseBlockType.get_blocks_stopwords()

        key = re.sub(r'\([^()]*\)', '', key).lower()

        for block in blocks:
            for word in blocks[block]:
                if word in key.lower():
                    return block

        return None

    def parse(self):
        tables = []
        with pdfplumber.open(self.order_path) as pdf:
            for page in pdf.pages:
                for row in page.extract_tables():
                    if row[0][0] == 'Компонент метаданных':
                        continue

                    for item in row:
                        cleaned_item = [c.replace("\n", "") for c in item if type(c) == str]

                        if len(cleaned_item) > 0:
                            tables.append(cleaned_item)

        tagged = {}
        main_structure = [row[0] for row in tables if len(row) == 1]
        numbers = [key for key, row in enumerate(tables) for item in main_structure if item in row]

        for key, num in enumerate(numbers):
            block = self.__define_block_name(main_structure[key])
            if block:
                self.blocks.append(CourseBlock(block, main_structure[key]))
                tagged.update({
                    block: tables[num + 1:numbers[key + 1]] if key + 1 < len(numbers) else tables[num + 1:]
                })

        stats = {}
        stops = ActivityType.get_normalized_stop_words()
        for block in tagged:
            for row in tagged[block]:
                for element in stops:
                    for word in stops[element]:
                        if ' '.join(row).lower().find(word) > 0:
                            item = self.__get_course_element(element, row)
                            if item:
                                if block not in stats.keys():
                                    stats.update({block: [item]})
                                else:
                                    stats[block].append(item)
                            break

        return stats
