from flask import Flask, render_template
from flask import request

from cor_quantity.forms import CORForm

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def check():
    from core.utils import check
    if request.method == 'GET':
        return render_template('index.html', form=CORForm())

    result = check(request)
    return render_template("done.html", result=result)


if __name__ == '__main__':
    app.run()
