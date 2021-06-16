from wtforms import Form, FileField
from wtforms.validators import InputRequired


class CORForm(Form):
    order = FileField('Прикрепите .pdf-файл регламента', [InputRequired()])
    cor = FileField('Прикрепите .mbz-файл ЦОРа', [InputRequired()])
