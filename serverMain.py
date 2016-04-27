import subprocess
import os
import smtplib
import shutil

from flask import Flask, request, send_file
from werkzeug import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

ALLOWED_EXTENSIONS = set(['txt', 'xmi'])

# https://www.google.com/settings/security/lesssecureapps
# Use to allow login from this application
gmail_user = "umlgenerator@gmail.com"
gmail_pwd = "umlUMLGen"
imageName = "testImage.png"

app = Flask(__name__)

@app.route("/")
def hello():
	return "Add /uml to the end of the address to generate UML!"

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload/<user>", methods=['GET', 'POST'])
def generateUML(user):
	if request.method == 'POST':
		plantFile = request.files['plantUML']
		xmiFile = request.files['xmi']
		if plantFile and xmiFile:
			plantFileName = secure_filename(plantFile.filename)
			plantFile.save(app.config["DIR"] + "/" + plantFileName)
			plantFilePath = app.config["DIR"] + "/" + plantFileName

			xmiFileName = secure_filename(xmiFile.filename)
			xmiFile.save(app.config["DIR"] + "/" + xmiFileName)
			xmiFilePath = app.config["DIR"] + "/" + xmiFileName

			plantUMLCommand = ["java", "-jar", "./plantuml.jar", plantFilePath]
			p = subprocess.call(plantUMLCommand)
			pngFileName = plantFileName.replace(".txt", ".png")
			pngFile = open(pngFileName, "r")
			# return send_file(pngFileName, mimetype='image/png')
			return sendMailToUser(user, plantFileName, xmiFileName)

	return "Error? How do I handle this?"

def sendMailToUser(user, plantFilePath, xmiFilePath):
	directory = user + "_UMLDiagram"

	if not os.path.exists(directory):
		os.makedirs(directory)

	newImageName = plantFilePath + ".png"
	curPathImage = "./" + newImageName
	newPathImage = directory + "/" + newImageName
	os.rename(curPathImage, newPathImage)

	curPathXMI = "./" + xmiFilePath
	newPathXMI = directory + "/" + xmiFilePath
	os.rename(curPathXMI, newPathXMI)

	zippedFile = directory + ".zip"

	shutil.make_archive(directory,'zip', directory)

	mail(user, "UML Diagram", "Attached is your picture!", zippedFile)
	return "Your email is being sent to " + user


def mail(to, subject, text, attach):
	msg = MIMEMultipart()

	msg['From'] = gmail_user
	msg['To'] = to
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	part = MIMEBase('application', 'octet-stream')
	part.set_payload(open(attach, 'rb').read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition',
		'attachment; filename="%s"' % os.path.basename(attach))
	msg.attach(part)

	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	# Should be mailServer.quit(), but that crashes...
	mailServer.close()


if __name__ == "__main__" :
	app.config["DIR"] = os.getcwd()
	app.run(debug="True")
