import re
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

from cor_quantity.pattern import Pattern


class CourseElement:
    def __init__(self, count=1):
        self.count = count
        super().__init__()

    def read(self):
        ...

    @staticmethod
    def preprocess(text):
        if type(text) == list:
            text = " ".join(re.findall(Pattern.RUSSIAN_LETTERS, text))
        doc = re.sub(Pattern.TO_LEMMATIZE, ' ', text)
        morph = MorphAnalyzer()
        tokens = []
        for token in doc.split():
            if token and token not in stopwords.words("russian"):
                token = token.strip()
                token = morph.normal_forms(token)[0]
                tokens.append(token)

        return tokens

