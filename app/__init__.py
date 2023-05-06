import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from .tasks import cn2, return_rules
import pandas as pd

app = Flask(__name__)

app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)
print(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = {'csv', 'txt'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    file = None
    attributes = None
    target_attr = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = None
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            data = pd.read_csv(file)
            attributes = data.columns.values.tolist()[:-1]
            attrs = attributes.copy()
            target_attr = data.columns.values.tolist()[-1]
            rules = cn2(data.to_dict('records'), attributes, target_attr)
            rules, default_rule, default_conclusion = return_rules(rules)
            print(rules)
            # default_rule = pd.DataFrame(default_rule)
            return render_template("rules.html", title='RESULTS', attributes=attrs, target_attr=target_attr, rules=rules) # tables=[default_rule.to_html(classes='data')], titles=default_rule.columns.values, default_conclusion=default_conclusion)
    return '''
    <!DOCTYPE html>
        <html>

        <head>
            <title>Upload new File</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #F6F6F6;
                    text-align: center;
                    margin-top: 50px;
                }

                h1 {
                    color: #333333;
                }

                form {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                    display: inline-block;
                    margin: 0 auto;
                    padding: 20px;
                    box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
                }

                input[type="file"] {
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    display: block;
                    font-size: 14px;
                    margin: 0 auto 20px auto;
                    padding: 10px;
                    width: 300px;
                }

                input[type="submit"] {
                    background-color: #1E90FF;
                    border: none;
                    border-radius: 5px;
                    color: #FFFFFF;
                    cursor: pointer;
                    font-size: 16px;
                    margin-bottom: 20px;
                    padding: 10px 20px;
                    transition: background-color 0.3s ease;
                }

                input[type="submit"]:hover {
                    background-color: #0080FF;
                }
            </style>
        </head>

        <body>
            <h1>Upload new File</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" id="file">
                <input type="submit" value="Upload">
            </form>
        </body>

        </html>
    '''
