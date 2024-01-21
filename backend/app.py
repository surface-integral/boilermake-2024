from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'backend/saved_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_file():
    # Check if the POST request has a file part
    if 'file' not in request.files:
        return render_template('invalid_file.html')
    
    file = request.files['file']

    if not allowed_file(file.filename):
        return render_template('invalid_file.html')
    
    # If the user does not select a file, return page indicating an error
    if file.filename == '':
        return render_template('no_file.html')
    
    # Save the uploaded file to the uploads folder
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        print(file.filename)
        return render_template('index.html', file=filename)

if __name__ == '__main__':
    # Ensure the 'uploads' folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
