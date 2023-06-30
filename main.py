# import requirements needed
import os, shutil
# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session, flash
from url_utils import get_base_url
import requests
from werkzeug.utils import secure_filename
import urllib.parse
import requests
# import roboflow
# from roboflow import Roboflow
import base64
import urllib.parse
import requests
from flask import request as flask_request
# from roboflow import Roboflow

# setup the webserver + API calls
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)
API_URL = "https://classify.roboflow.com/greenai-v2-v4sv0/2"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
parameters = {"api_key": "9XoKpVqEjfVLCDsiYYLx"}
rec_type = ""

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#clears uploads folder on flask app run
for filename in os.listdir(UPLOAD_FOLDER):
  file_path = os.path.join(UPLOAD_FOLDER, filename)
  try:
    if os.path.isfile(file_path) or os.path.islink(file_path):
      os.unlink(file_path)
    elif os.path.isdir(file_path):
      shutil.rmtree(file_path)
  except Exception as e:
    print('Failed to delete %s. Reason: %s' % (file_path, e))

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
  app = Flask(__name__)
  requests.post(API_URL,
                headers=headers,
                data=None,
                json={"wait_for_model": True})
else:
  app = Flask(__name__, static_url_path=base_url + 'static')
  requests.post(API_URL,
                headers=headers,
                params=parameters,
                data=None,
                json={"wait_for_model": True})

# adds upload folder to base app directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(64)


# set up the routes and logic for the webserver
@app.route(f'{base_url}')
def home():
  # session["data"] = "genre_guess_label"

  rec_type = "The image belongs to class with confidence score og"
  return render_template('index.html', genre="no image uploaded")


# tests if file is a valid extension
def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(f'{base_url}', methods=['POST'])
def upload_file():
  try:
    global rec_type
    rec_type = "new val"

    print("uploading?")
    # session["data"] = "genre_guess_label"
    rec_type = "genre_guess_label"
    print("reached to upload section")
    if flask_request.method == 'POST':
      print("reached to post method")
      if 'file' not in flask_request.files:
        print("reached to file found")
        flash('no file part')
        return redirect(url_for('home'))

      file = flask_request.files['file']
      print("reached to post method 2")
      if file.filename == '':
        print("reached to file not present")
        flash("no selected file")
        return redirect(url_for('home'))
      # else:
      #   return redirect(url_for('home'))

      if file and allowed_file(file.filename):
        print("reached to file present")
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with open(f'uploads/{filename}', 'rb') as image_file:
          image_base64 = image_file.read()
          image = base64.b64encode(image_base64).decode('utf-8')

          url = "https://classify.roboflow.com/greenai-v2-v4sv0/2"
          params = {"api_key": "9XoKpVqEjfVLCDsiYYLx"}
          headers = {"Content-Type": "application/x-www-form-urlencoded"}

          response = requests.post(url,
                                   params=params,
                                   data=image,
                                   headers=headers)

          if response.status_code == 200:
            result = response.json()
            print(result)
            genre_class = result["predictions"][0]['class']
            genre_score = result["predictions"][0]['confidence']
            genre_score *= 100

            genre_score = '%.2f' % genre_score
            # genre_label = result[0]['label']
            genre_guess_label = f'{genre_score}% '
            print("reached to correct response")
            print("genre_guess_label")
            print("reached to correct response 2")
            rec_type = genre_guess_label

            if genre_class == "Paper":
              return redirect(
                url_for('paper_results', resulting_string=rec_type))
            elif genre_class == "Compost":
              return redirect(
                url_for('compost_results', resulting_string=rec_type))
            elif genre_class == "Plastic":
              return redirect(
                url_for('plastic_results', resulting_string=rec_type))
            elif genre_class == "Glass":
              return redirect(
                url_for('glass_results', resulting_string=rec_type))
            elif genre_class == "Metal Waste":
              return redirect(
                url_for('metal_results', resulting_string=rec_type))
            elif genre_class == "RC":
              return redirect(url_for('rc_results', resulting_string=rec_type))
            else:
              return redirect(
                url_for('undetectable_results', resulting_string=rec_type))

          else:
            print("reached to api error")
            print("API error occurred:", response.text)
            flash(
              'API error has occurred, wait a few seconds and try again...')
            return redirect(url_for('home'))
  except:
    return redirect(url_for('home'))


# {'time': 0.19405875699976605, 'image': {'width': 450, 'height': 296}, 'predictions': [{'class': 'Paper', 'confidence': 0.9728}, {'class': 'RC', 'confidence': 0.0075}, {'class': 'Compost', 'confidence': 0.0054}, {'class': 'Plastic', 'confidence': 0.0051}, {'class': 'Metal Waste', 'confidence': 0.0038}, {'class': 'Glass', 'confidence': 0.0029}, {'class': 'DNR', 'confidence': 0.0025}], 'top': 'Paper', 'confidence': 0.9728}

# https://replit.com/join/ckmmrlxwoi-ashishsutariya


@app.route(f'{base_url}/results')
def results():
  return render_template('results.html', resulting_string=rec_type)


@app.route(f'{base_url}/paper_results')
def paper_results():
  return render_template('paper_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/plastic_results')
def plastic_results():
  return render_template('plastic_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/glass_results')
def glass_results():
  return render_template('glass_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/compost_results')
def compost_results():
  return render_template('compost_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/metal_results')
def metal_results():
  return render_template('metal_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/rc_results')
def rc_results():
  return render_template('rc_results.html', resulting_string=rec_type)


@app.route(f'{base_url}/undetectable_results')
def undetectable_results():
  return render_template('undetectable_results.html',
                         resulting_string=rec_type)


def query(filename):
  with open(filename, "rb") as f:
    data = f.read()
    json = {"wait_for_model": True}
  response = requests.post(API_URL, headers=headers, data=data, json=json)
  return response.json()


if __name__ == '__main__':
  # IMPORTANT: change url to the site where you are editing this file.
  website_url = 'computer-vision-module-smalling.2023-instructor-crash-course.repl.co'

  print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
  app.run(host='0.0.0.0', port=port, debug=True)
