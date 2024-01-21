from flask import Flask, render_template, request, redirect
from string_parser import parse_problem, determine_type_add
import os
from PIL import Image

import sys
sys.path.append('/Users/aht_2004/boilermake-2024/')
import main 


app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'backend/saved_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

text_prompts = []


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_file():
    # Check if the POST request has a file part
    if 'file-input' not in request.files:
        return render_template('invalid_file.html')

    file = request.files['file-input']

    if not allowed_file(file.filename):
        return render_template('invalid_file.html')
    
    # If the user does not select a file, return page indicating an error
    if file.filename == '':
        return render_template('no_file.html')
    
    # Save the uploaded file to the uploads folder
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        print("test")
        problem_type = det
        return render_template('image_loaded.html', file=filename)

@app.route("/upload_text", methods=["POST"])
def upload_text():
    text = request.form['text-input']
    text_prompts.append(text)
    print(text_prompts[0])
    problem_type = determine_type_add(text_prompts)
    parsed_data = parse_problem(text_prompts[0], "Addition", problem_type) 
    print("subject 1: "+str(parsed_data["Subject1"]))
    print(parsed_data)
    return render_template('image_loaded.html')



if __name__ == '__main__':
    # Ensure the 'uploads' folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
