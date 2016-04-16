from flask import Flask, request, send_file
from werkzeug import secure_filename
import subprocess
import os

ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)

@app.route("/")
def hello():
	return "Add /uml to the end of the address to generate UML!"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def generateUML():
	if request.method == 'POST':
		plantFile = request.files['file']
		if plantFile and allowed_file(plantFile.filename):
			plantFileName = secure_filename(plantFile.filename)
			plantFile.save(app.config["DIR"] + "/" + plantFileName)
			plantFilePath = app.config["DIR"] + "/" + plantFileName
			plantUMLCommand = ["java", "-jar", "./plantuml.jar", plantFilePath]
			p = subprocess.call(plantUMLCommand)
			pngFileName = plantFileName.replace(".txt", ".png")
			pngFile = open(pngFileName, "r")
			return send_file(pngFileName, mimetype='image/png')
			# return send_file(pngFileName)

	return "Error? How do I handle this?"

if __name__ == "__main__" :
	app.config["DIR"] = os.getcwd()
	app.run()
