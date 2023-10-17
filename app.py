from flask import send_file,render_template, Response, Flask, request
import uuid
from io import BytesIO
from db.queries import *
import db.model as dbm
from db.database import *
from generate_frames import *

app = Flask(__name__)
dbm.Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store_url', methods=["POST"])
def store_url():
    Url = request.form['urlLink']
    
    random_uuid = uuid.uuid4()
    insert_id_database(id=str(random_uuid),url=Url)
    print(f'url saved successfully: {random_uuid}')
    return render_template("home.html", id_uuid = random_uuid)

@app.route('/home/<id_uuid>', methods=["GET"])
def home(id_uuid):
    return render_template('home.html', id_uuid=id_uuid)

@app.route('/generate_frame/<id_uuid>')
def generate_frame(id_uuid):
    return Response(generate_frames(id_uuid),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed/<id_uuid>', methods=["GET"])
def video_feed(id_uuid):
    return render_template("home.html", id_uuid=id_uuid)

@app.route('/frame_feed/<id_uuid>')
def frame_feed(id_uuid):
    return Response(generate_ss(id_uuid), 
                    mimetype='multipart/x-mixes-replace; boundary=frame')

@app.route('/set_area/<id_uuid>')
def set_area(id_uuid):
    ss = frame_feed(id_uuid)
    return render_template('set_area.html', id_uuid=id_uuid)

@app.route('/get_image/<id_uuid>')
def get_image(id_uuid):
    ss = get_img(id=id_uuid)
    return send_file(BytesIO(ss), mimetype='image/jpeg')

@app.route('/store_number_area/<id_uuid>', methods=['GET','POST'])
def store_number_area(id_uuid):
    if request.method == 'POST':
        frame_feed(id_uuid)
        number = int(request.form['number'])
        insert_area(id_uuid=id_uuid,area=number)
        print(f'number succesfuly be saved: {number}')
        return '',204
    return 'this is a get request'

@app.route('/save_coordinates/<id_uuid>', methods=['POST'])
def save_coordinates(id_uuid):
    all_coords = []
    data = request.get_json()
    coordinates = data['coordinates']
    all_coords.append(coordinates)
    insert_coordinates(id_uuid=id_uuid,coordinates=coordinates)
    return all_coords

@app.route('/send_database/<id_uuid>', methods=["GET","POST"])
def send_database(id_uuid):
    data = save_coordinates()
    if request.method == 'POST':
        insert_coordinates(id_uuid=id_uuid, coordinates=data)
        print(f'now: {data}')
        return '', 204
    return "get request"

@app.route('/area_coordinates/<id_uuid>')
def area_coordinates(id_uuid):
    return render_template('area_coordinate.html', id_uuid=id_uuid)

@app.route('/video_feed_area/<id_uuid>', methods=['GET'])
def video_feed_area(id_uuid):
        return Response(generate_frames_area(id_uuid),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__" :
    app.run(debug=True, port=8080)