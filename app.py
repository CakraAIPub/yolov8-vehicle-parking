from flask import send_file,render_template, Response, Flask, request, jsonify
from flask_socketio import SocketIO

from ultralytics import YOLO
import cv2
import cvzone
import numpy as np

from io import BytesIO
import uuid
from db.queries import *
import db.model as dbm
from db.database import *


app = Flask(__name__)
dbm.Base.metadata.create_all(bind=engine)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

################# function video processing #########################
model = YOLO('yolov8n.pt')

#function send space to frontend
def send_space(space):
    socketio.emit('space_update',{'space': space})

#functio to generate cctv frame without object detection model
def generate_frames(id_uuid):
    url = get_url(id_uuid)
    cap = cv2.VideoCapture(url)
    
    while cap.isOpened():
        success, frame = cap.read()

        if success:
            #encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            #yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            #break the loop if the end of the video is reached
            break

#function for generate screenshoot of video for setting areas
def generate_ss(id_uuid):
    url = get_url(id_uuid)
    cap = cv2.VideoCapture(url) 
    succes, frame = cap.read()
    frame = cv2.resize(frame, (1280,720))
    if succes:
        screenshoot_data = cv2.imencode('.jpg', frame)[1].tobytes()
        insert_image(id_uuid=id_uuid, url_imgae=screenshoot_data)
        return "Image saved to database succesfuly"
    return "Failed to save the image"

#function for generating frame cctv with object detection model
def generate_frames_area(id_uuid):
    url = get_url(id_uuid)
    cap = cv2.VideoCapture(url)

    areas = get_coords(id=id_uuid)

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            frame = cv2.resize(frame,(1280,720))
            space_occupancy = [0] * len(areas)
            results = model.predict(frame, classes=[2,7])
            for result in results:
                boxes = result.boxes.data.to('cpu').numpy().astype(int)
                for box in boxes:
                    x1,y1,x2,y2 = box[0], box[1], box[2], box[3]
                    cx = int(x1+x2)//2
                    cy = int(y1+y2)//2

                    for i,area in areas.items():
                        result_pol = cv2.pointPolygonTest(np.array(area,np.int32),(cx,cy),False)
                        if result_pol >=0:
                            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            # cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                            space_occupancy[i] = 1

            # for area_coords in areas.values():
            #     area_coords_np = np.array(area_coords, np.int32).reshape((-1, 1, 2))
            #     cv2.polylines(frame, [area_coords_np], isClosed=True, color=(1, 1, 1), thickness=2)

            space = space_occupancy.count(0)
            send_space(space=space)
            # cvzone.putTextRect(frame, f' {str(areas)}', (50,50),1,1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break

#################### route ####################################

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
    coordinates = get_coords(id_uuid)
    return render_template('area_coordinate.html', id_uuid=id_uuid, coordinates_json=coordinates)

@app.route('/toggle_yes_no/<id_uuid>', methods=['POST'])
def toggle_yes_no(id_uuid):
    return '', 204

@app.route('/get_coordinates/<id_uuid>')
def get_coordinates(id_uuid):
    coordinates = get_coords(id_uuid)
    return jsonify(coordinates)

@app.route('/video_feed_area/<id_uuid>', methods=['GET'])
def video_feed_area(id_uuid):
        return Response(generate_frames_area(id_uuid),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__" :
    app.run(debug=True, port=8080)