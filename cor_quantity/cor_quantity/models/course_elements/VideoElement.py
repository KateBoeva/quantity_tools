import re

from youtube_easy_api.easy_wrapper import YoutubeEasyWrapper

from config import API_KEY
from cor_quantity.models.course_elements.CourseElement import CourseElement
from cor_quantity.pattern import Pattern


from urllib import parse


class VideoElement(CourseElement):
    def __init__(self, min_d, max_d, module, count, link=''):
        self.min_d = min_d
        self.max_d = max_d
        self.module = module
        if module != 'order':
            self.link = link
            self.duration = self.get_duration()
        super().__init__(count)

    def read(self):
        easy_wrapper = YoutubeEasyWrapper()
        easy_wrapper.initialize(api_key=API_KEY)
        video_id = parse.parse_qs(parse.urlsplit(self.link).query)['v'][0]
        return easy_wrapper.get_metadata(video_id=video_id)

    def get_duration(self):
        duration = self.read()['contentDetails']['duration']
        return re.findall(Pattern.NUMBER, duration)[0]
