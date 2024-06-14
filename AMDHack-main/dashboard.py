from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from generate_scan import generate_html_report  # Adjust this import based on your project structure
import re, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure a directory to save uploaded files
UPLOAD_FOLDER = 'scans'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def main_page():
    # Example projects list
    projects = ['TensorFlow']
    return render_template('main_page.html', projects=projects)

@app.route('/project/<project_name>')
def project_pipelines(project_name):
    # Example pipelines for a project
    pipelines = [f for f in os.listdir('scans') if f.endswith('.sarif')]
    return render_template('project_pipelines.html', project_name=project_name, pipelines=pipelines)

@app.route('/pipeline/<pipeline_name>')
def pipeline_sarif_report(pipeline_name):
    # Assuming the JSON file name is based on the pipeline_name
    json_file = f'scans/{pipeline_name}'
    html_filename = f'sarif_report_{pipeline_name}.html'  # Just the filename, no directory
    output_file = f'static/{html_filename}'  # Full path for internal use
    match = re.search(r'-(\w+)-', pipeline_name)
    hash_value = match.group(1)
    commit_link = f'https://github.com/tensorflow/tensorflow/commit/{hash_value}'

    # Generate the HTML report
    generate_html_report(json_file, output_file, commit_link, hash_value)

    # Assuming the HTML file is saved in a directory named 'static'
    return send_from_directory('static', html_filename)

@app.route('/upload_sarif/<project_name>', methods=['POST'])
def upload_sarif(project_name):
    if 'sarif_file' not in request.files:
        return redirect(request.url)
    file = request.files['sarif_file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.sarif'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Optionally, generate a new HTML report for the uploaded SARIF file here
        return redirect(url_for('project_pipelines', project_name=project_name))
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)