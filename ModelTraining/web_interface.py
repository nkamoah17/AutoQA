from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import git

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('/path/to/save/files', filename))
                return redirect(url_for('uploaded_file', filename=filename))
        elif 'github_url' in request.form:
            github_url = request.form['github_url']
            if github_url:
                git.Git("/path/to/save/files").clone(github_url)
                return 'Github repo cloned successfully!'
    return '''
    <!doctype html>
    <title>Upload a File</title>
    <style>
        body {
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        h1 {
            color: #333;
        }
        form {
            margin: 20px 0;
        }
    </style>
    <h1>Upload a File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <h1>Or</h1>
    <form method=post>
      <input type=text name=github_url placeholder='Enter Github repo URL'>
      <input type=submit value=Clone>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)