import os
import re
import shutil
from xml.dom import minidom

from pptx import Presentation

from cor_quantity.models.types.ActivityType import ActivityType
from cor_quantity.models.course_elements.FileElement import FileElement
from cor_quantity.models.course_elements.LectureElement import LectureElement
from cor_quantity.models.course_elements.PresentationElement import PresentationElement
from cor_quantity.models.course_elements.RPDElement import RPDElement
from cor_quantity.models.course_elements.TextElement import TextElement
from cor_quantity.models.course_elements.VideoElement import VideoElement
from cor_quantity.models.types.CourseBlockType import CourseBlockType
from cor_quantity.parsers.Parser import Parser
from cor_quantity.pattern import Pattern
from core.const import RAW_COR, TMP_DIR


class CourseParser(Parser):
    def __init__(self, main_file, cor_path):
        self.main_file = main_file
        self.cor_path = cor_path

    @staticmethod
    def parse_raw_file(filename):
        parsed = minidom.parse(filename)
        parsed.normalize()
        return parsed

    @staticmethod
    def get_tags_data(tag, xml_file, attrs=None):
        raw_data = xml_file.getElementsByTagName(tag)
        data = []

        for element in raw_data:
            item = {}
            for child in element.childNodes:
                if child.nodeName != "#text":
                    try:
                        item.update({
                            child.nodeName: child.childNodes[0].nodeValue
                        })
                    except IndexError:
                        continue

                if attrs:
                    for attr in attrs:
                        try:
                            item.update({
                                attr: element.getAttribute(attr)
                            })
                        except AttributeError:
                            continue

            if len(item) > 0:
                data.append(item)

        return data

    def get_subjects(self):
        sections = self.get_tags_data('section', self.main_file)
        subjects = []

        for section in sections:
            module = CourseBlockType.get_block_type(section['title'])
            if module == CourseBlockType.SUBJECT:
                subjects.append(section['title'])

        return subjects

    def __get_activities_by_section(self, section_id, activity_list):
        result = []
        file_names = {}

        data_files = self.parse_raw_file(RAW_COR + 'files.xml')
        files = self.get_tags_data('file', data_files)

        for dirpath, dirnames, filenames in os.walk(RAW_COR + "files"):
            for dirname in dirnames:
                file_names.update({dirname: ''})
            for filename in filenames:
                for directory in file_names.keys():
                    if filename.startswith(directory):
                        file_names[directory] = filename

        for key, file in enumerate(files):
            if file['contenthash'] not in file_names.values():
                del files[key]

        def get_file_data(filename, files):
            for file in files:
                if file['contenthash'] == filename:
                    return file

        def get_file_by_context(context_id, files):
            for file in files:
                if file['contextid'] == str(context_id):
                    return file

            return None

        for dirname in file_names:
            try:
                shutil.copy(RAW_COR + 'files/' + dirname + '/' + file_names[dirname],
                            TMP_DIR + get_file_data(file_names[dirname], files)['filename'])
            except:
                continue

        for activity in activity_list:
            if activity['sectionid'] == section_id:
                xml_path = RAW_COR + activity['directory'] + '/' + activity['modulename'] + '.xml'
                activity_file = self.parse_raw_file(xml_path)
                data = activity_file.getElementsByTagName('activity')[0]
                try:
                    content = activity_file.getElementsByTagName('intro')[0].firstChild.nodeValue
                except:
                    content = ''

                activity.update({
                    'file': get_file_by_context(data.getAttribute('contextid'), files),
                    'content': re.sub(r'\<[^>]*\>', '', content)
                })
                result.append(activity)

        return result

    def __define_structure(self):
        sections = self.get_tags_data('section', self.main_file)
        activities = self.get_tags_data('activity', self.main_file)

        structure = {}
        for block in CourseBlockType.get_block_types():
            structure.update({block: []})

        for section in sections:
            title = CourseBlockType.INTRO.value if section['title'] == '0' else section['title']
            module = CourseBlockType.get_block_type(section['title'])

            structure[module].append({
                'section_id': section['sectionid'],
                'section_title': title,
                'activities': self.__get_activities_by_section(section['sectionid'], activities)
            })

        return structure

    def parse(self):
        structure = self.__define_structure()
        elements = {}
        for block in CourseBlockType.get_block_types():
            elements.update({block: {}})

        for module in structure:
            for key, item in enumerate(structure[module]):
                items = []
                for activity in structure[module][key]['activities']:
                    if activity['modulename'] == 'label':
                        link = re.search(Pattern.LINK, activity['title'])
                        if link:
                            link = link.string[:link.string.find('&nbsp;')]
                            items.append(VideoElement(None, None, module, 1, link))
                        else:
                            items.append(TextElement(activity['title'], activity['content']))
                    elif activity['file']:
                        if activity['file']['filename'].endswith('.pptx'):
                            prs = Presentation(TMP_DIR + activity['file']['filename'])
                            items.append(PresentationElement(None, None, 1, prs))
                        if activity['title'].lower() in ActivityType.get_stop_words(ActivityType.RPD):
                            items.append(RPDElement(TMP_DIR + activity['file']['filename']))
                        elif activity['file']['filename'].endswith('.pdf'):
                            items.append(FileElement(TMP_DIR + activity['file']['filename']))
                    elif activity['modulename'] == 'lesson':
                        items.append(LectureElement(activity['title'], activity['content']))
                    elif activity['modulename'] == 'quiz':
                        quiz_xml = RAW_COR + activity['directory'] + "/" + activity['modulename'] + '.xml'
                        from cor_quantity.models.course_elements.TestElement import TestElement
                        items.append(TestElement(quiz_xml))

                elements[module].update({structure[module][key]['section_title']: items})

        return elements
