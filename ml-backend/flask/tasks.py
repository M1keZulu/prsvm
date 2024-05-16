import json
import cv2
import time
import numpy as np
import uuid
import openvino.runtime as ov
import tqdm
from sklearn.metrics.pairwise import cosine_similarity

def generate_reid_video(filenames, query):
    core = ov.Core()
    model = core.read_model("/Users/zain/Downloads/Person_ReID_Testing/dataset-generation-tool/models/person-reidentification-retail-0277/person-reidentification-retail-0265.onnx")
    reid_model = core.compile_model(model, "CPU")

    print("Generating reid video")
    #read query image
    query_image = cv2.imread(query)
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

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    filename = "database/incidents/"+uuid.uuid4().hex+".mp4"
    out = cv2.VideoWriter(filename, fourcc, 30.0, (1280, 720))

    for file in filenames:
        with open("database/"+file+"/"+file+".json", "r") as f:
            json_data = json.load(f)
        for detection in json_data["detections"]:
            detection["distance"] = cosine_similarity(np.array(detection["reid"]).reshape(1, -1), query_reid.reshape(1, -1))[0][0]
        pbar = tqdm.tqdm(total=len(json_data["detections"]), desc=file)
        #for each detection compare with query image and add frame to video if distance is less than threshold
        cap = cv2.VideoCapture("database/"+file+"/"+file)
        # if cosine distance between query and image is less than 0.5, get frame from video and add to output video
        for detection in json_data["detections"]:
            if detection["distance"] > 0.5:
                pbar.update(1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, detection["frame"])
                ret, frame = cap.read()
                if ret:
                    cv2.rectangle(frame, (detection["xmin"], detection["ymin"]), (detection["xmax"], detection["ymax"]), (0, 255, 0), 2)
                    #write frame as 1280x720
                    frame = cv2.resize(frame, (1280, 720))
                    out.write(frame)

        pbar.close()
        cap.release()
    out.release()
    return filename





def process_video(filename, timestamp):
    core = ov.Core()
    model = core.read_model("/Users/zain/prsvm/ml-backend/flask/person-detection-retail-0013/FP16-INT8/person-detection-retail-0013.xml")
    detection_model = core.compile_model(model, "CPU")
    model = core.read_model("/Users/zain/Downloads/Person_ReID_Testing/dataset-generation-tool/models/person-reidentification-retail-0277/person-reidentification-retail-0265.onnx")
    reid_model = core.compile_model(model, "CPU")

    print("Processing video: ", filename)
    video_path = "database/"+filename+"/"+filename
    cap = cv2.VideoCapture(video_path)
    pbar = tqdm.tqdm(total=cap.get(cv2.CAP_PROP_FRAME_COUNT), desc=filename)
    json_data = {"timestamp": timestamp, "detections": []}
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        pbar.update(1)
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
                
                json_data["detections"].append({
                    "frame": int(cap.get(cv2.CAP_PROP_POS_FRAMES)),
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax,
                    "reid": reid_result.tolist()[0]
                })
    pbar.close()
    cap.release()

    with open("database/"+filename+"/"+filename+".json", "w") as f:
        json.dump(json_data, f)
    pbar.close()
    cap.release()


if __name__ == "__main__":
    generate_reid_video(["Walking_1_basketballcourt.mp4", "Walking_2_Basketballcourt.mp4", "Walking_3_Backyard.mp4", "Walking_4_Backyard.mp4", "Walking_5_Backyard.mp4", "Walking_5_Cam_Back_yard.mp4", "Walking_6_CSBlockEntrance.mp4"], "/Users/zain/Desktop/Screenshots/Screenshot 2023-11-21 at 6.51.40 PM.png")