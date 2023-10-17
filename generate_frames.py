from ultralytics import YOLO
import cv2
import cvzone
import numpy as np
from db.queries import *

model = YOLO('yolov8n.pt')

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
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                            space_occupancy[i] = 1

            for area_coords in areas.values():
                area_coords_np = np.array(area_coords, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [area_coords_np], isClosed=True, color=(1, 1, 1), thickness=2)

            space = space_occupancy.count(0)
            cvzone.putTextRect(frame, f'sisa parkir: {str(space)}', (50,50),1,1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break