class Pattern:
    VIDEO_DURATION = 'Длительность\s+\-\s+\d+((\-\d)*|\d+)\s+минут'
    VIDEO_EXTREME = '[А-я]\s*[А-я]\D+\s+\d+((\-\d)*|\d+)\s+минут'
    VIDEO_COUNT = '[А-я]\s*[А-я]\D+\s+\d+\s+(ролик|видео)'
    NUMBER = '\d+'
    PRESENTATION_COUNT = '[А-я]\s*[А-я]\D+\s+\d+\s+презентац'
    PRES_SLIDES_COUNT = '[А-я]\D+\s+\d+\s+слайдов'
    LINK = '(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?'
    TO_LEMMATIZE = "[A-Za-z0-9!#$%&'()*+,./:;<=>«»?@[\]^_`{|}~—\"\-]+"
    RUSSIAN_LETTERS = "[а-яА-Я]+"
    RPD_THEME_HEADER = 'Тема\s{1,4}\d{1,2}.'
    RPD_THEME = "(.\n|\n)[A-Za-zА-я0-9!#$%&'()*+,.\/:;<=>«»?@[\]^_{|}~—\"\- ]+"
    TIME = "\(([0-9]+.*?)\)"
