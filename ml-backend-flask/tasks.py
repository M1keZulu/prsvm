import json
import cv2
import time
import numpy as np
import uuid
import openvino.runtime as ov
import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO, send, emit

load_dotenv()

def generate_reid_video(filenames, video_name, timestamp, height, width, x, y, job_id):
    core = ov.Core()
    model = core.read_model(os.getenv("REID_MODEL"))
    reid_model = core.compile_model(model, "CPU")

    print("Generating reid video")

    #extract query image from video
    ext = video_name.split(".")[-1]
    video_path = "database/"+video_name+"/"+"video."+ext
    cap = cv2.VideoCapture(video_path)
    timestamp_in_milliseconds = float(timestamp) * 1000
    cap.set(cv2.CAP_PROP_POS_MSEC, int(timestamp_in_milliseconds))
    ret, frame = cap.read()
    if not ret:
        return
    
    cv2.imwrite("database/incidents/"+job_id+".jpg", frame[int(y):int(y)+int(height), int(x):int(x)+int(width)])

    query_image = frame[int(y):int(y)+int(height), int(x):int(x)+int(width)]
    if query_image.size == 0:
        return
    query_image = cv2.resize(query_image, (128, 256))
    query_image = query_image.transpose((2, 0, 1))
    reid_request = reid_model.create_infer_request()
    query_image = query_image.reshape(1, *query_image.shape)
    query_image = query_image.astype(np.float32)
    reid_request.set_tensor("data", ov.Tensor(query_image))
    reid_request.infer()

    reid_request.wait()

    output_layer = reid_model.output(0)
    query_reid = reid_request.get_output_tensor(output_layer.index).data

    fourcc = cv2.VideoWriter_fourcc(*'H264')

    if not os.path.exists("database/incidents"):
        os.makedirs("database/incidents")
    filename = "database/incidents/"+job_id+".mp4"
    out = cv2.VideoWriter(filename, fourcc, 5.0, (1280, 720))

    videos_detected = {}
    images_list = []

    total_detections = 0
    for file in filenames:
        with open("database/"+file+"/"+"detections.json", "r") as f:
            json_data = json.load(f)
        total_detections += len(json_data["detections"])
    
    count_detections = 0

    for file in filenames:
        with open("database/"+file+"/"+"detections.json", "r") as f:
            json_data = json.load(f)
        for detection in json_data["detections"]:
            detection["distance"] = cosine_similarity(np.array(detection["reid"]).reshape(1, -1), query_reid.reshape(1, -1))[0][0]
        pbar = tqdm.tqdm(total=len(json_data["detections"]), desc=file)
        #for each detection compare with query image and add frame to video if distance is less than threshold
        cap = cv2.VideoCapture("database/"+file+"/"+"video."+file.split(".")[-1])
        # if cosine distance between query and image is less than 0.5, get frame from video and add to output video
        for detection in json_data["detections"]:
            count_detections += 1
            progress = count_detections/total_detections * 100
            SocketIO(message_queue='redis://').emit("incidentprogress", {"job_id": job_id, "progress": progress})
            if detection["distance"] > 0.4:
                if file not in videos_detected:
                    videos_detected[file]=1
                else:
                    videos_detected[file]+=1
                #open image from detection['image']
                images_list.append(detection["image"])
                image = cv2.imread(detection["image"])
                image = cv2.resize(image, (1280, 720))
                #add image to output video
                out.write(image)
            pbar.update(1)

        pbar.close()
        cap.release()
    out.release()

    SocketIO(message_queue='redis://').emit("progress", {"job_id": job_id, "progress": 100, "videos_detected": videos_detected, "images_list": images_list})

    return

def process_video(filename, job_id):
    core = ov.Core()
    model = core.read_model(os.getenv("DETECTION_MODEL"))
    detection_model = core.compile_model(model, "CPU")
    model = core.read_model(os.getenv("REID_MODEL"))
    reid_model = core.compile_model(model, "CPU")

    print("Processing video: ", filename)
    ext = filename.split(".")[-1]
    video_path = "database/"+filename+"/"+"video."+ext
    cap = cv2.VideoCapture(video_path)
    pbar = tqdm.tqdm(total=cap.get(cv2.CAP_PROP_FRAME_COUNT), desc=filename)
    json_data = {"detections": []}
    no_of_detections=100
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        pbar.update(1)
        #skip frames if detections are low
        if no_of_detections < 10:
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES)+10)
        #SocketIO(message_queue='redis://').emit("progress", {"job_id": job_id, "progress": cap.get(cv2.CAP_PROP_POS_FRAMES)/cap.get(cv2.CAP_PROP_FRAME_COUNT) * 100})
        #get total progress
        progress = cap.get(cv2.CAP_PROP_POS_FRAMES)/cap.get(cv2.CAP_PROP_FRAME_COUNT) * 100
        SocketIO(message_queue='redis://').emit("vidprogress", {"job_id": job_id, "progress": progress})
        if ret and frame is not None and frame.size!=0:
            input_data = cv2.resize(frame, (544, 320))
            input_data = input_data.transpose((2, 0, 1))
            infer_request = detection_model.create_infer_request()
            input_data = input_data.reshape(1, *input_data.shape)
            input_data = input_data.astype(np.float32)
            infer_request.set_tensor("data", ov.Tensor(input_data))
            infer_request.infer()
            output_layer = detection_model.output(0)
            result = infer_request.get_output_tensor(output_layer.index).data

            detections = []
            for detection in result[0][0]:
                if detection[2] > 0.5:
                    detections.append(detection)

            no_of_detections = len(detections)
            

            for detection in detections:
                xmin = int(detection[3] * frame.shape[1])
                ymin = int(detection[4] * frame.shape[0])
                xmax = int(detection[5] * frame.shape[1])
                ymax = int(detection[6] * frame.shape[0])
                
                crop = frame[ymin:ymax, xmin:xmax]
                if crop.size == 0:
                    continue
                crop = cv2.resize(crop, (128, 256))
                crop = crop.transpose((2, 0, 1))
                reid_request = reid_model.create_infer_request()
                crop = crop.reshape(1, *crop.shape)
                crop = crop.astype(np.float32)
                reid_request.set_tensor("data", ov.Tensor(crop))
                reid_request.infer()

                output_layer = reid_model.output(0)
                reid_result = reid_request.get_output_tensor(output_layer.index).data

                #save image with bounding box and unique name
                image = frame.copy()
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                random_name = uuid.uuid4().hex
                cv2.imwrite("database/"+filename+"/"+random_name+".jpg", image)

                json_data["detections"].append({
                    "frame": int(cap.get(cv2.CAP_PROP_POS_FRAMES)),
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax,
                    "reid": reid_result.tolist()[0],
                    "image": "database/"+filename+"/"+random_name+".jpg"
                })

                
    SocketIO(message_queue='redis://').emit("vidfinish", {"job_id": job_id})
    pbar.close()
    cap.release()

    with open("database/"+filename+"/"+"detections.json", "w") as f:
        json.dump(json_data, f)
    pbar.close()
    cap.release()


if __name__ == "__main__":
    generate_reid_video(["Screencast 2023-12-04 23:36:40-1703604771595.mp4"], "/Users/zain/Desktop/Screenshots/Screenshot 2023-11-21 at 6.51.40 PM.png")