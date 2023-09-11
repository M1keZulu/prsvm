import cv2
import time
import numpy as np
import os
import uuid
from openvino.inference_engine import IECore
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import tqdm

def saveFeatures(video_folder_path):
    #for all videos in the database, save the features of all detections in a folder
    if not os.path.exists(video_folder_path):
        print("Video folder path does not exist")
        return

    video_list = os.listdir(video_folder_path)

    if video_list is None:
        print("Video folder is empty")
        return

    if not os.path.exists("features"):
        os.makedirs("features")
    if not os.path.exists("gallery"):
        os.makedirs("gallery")

    for video in video_list:
        video_path = os.path.join(video_folder_path, video)
        cap = cv2.VideoCapture(video_path)
        pbar = tqdm.tqdm(total=cap.get(cv2.CAP_PROP_FRAME_COUNT), desc=video)
        while True:
            ret, frame = cap.read()
            pbar.update(1)
            if not ret:
                break
            if ret and frame is not None and frame.size!=0:
                input_data = cv2.resize(frame, (544, 320))
                input_data = input_data.transpose((2, 0, 1))
                result = det_exec_net.infer(inputs={det_input_name: input_data})
                output = result[det_output_name]

                for detection in output[0][0]:
                    confidence = detection[2]
                    if confidence > 0.5:
                        xmin = int(detection[3] * frame.shape[1])
                        ymin = int(detection[4] * frame.shape[0])
                        xmax = int(detection[5] * frame.shape[1])
                        ymax = int(detection[6] * frame.shape[0])
                        cropped = frame[ymin:ymax, xmin:xmax]
                        if cropped.size == 0:
                            continue
                        cropped = cv2.resize(cropped, (128, 256))
                        cropped = cropped.transpose((2, 0, 1))
                        feature_result = reid_exec_net.infer(inputs={reid_input_name: cropped})
                        feature = feature_result[reid_output_name]
                        #filename should contain video name, frame number, and detection number
                        filename = video + "_" + str(int(cap.get(cv2.CAP_PROP_POS_FRAMES))) + "_" + str(uuid.uuid4())
                        np.save("features/" + filename, feature)
                        cv2.imwrite("gallery/" + filename + ".png", cropped.transpose((1, 2, 0)))
        pbar.close()


def searchFeatures(compare_image_path, feature_folder_path, gallery_folder_path, threshold=0.5):
    #for all features in the gallery, compare it with the feature of the query
    #if the similarity is greater than a threshold, then cropped the detection and save it in a folder

    if not os.path.exists(compare_image_path):
        print("Search image path does not exist")
        return

    compare_input = cv2.imread(compare_image_path)
    compare_input = cv2.resize(compare_input, (128, 256))
    compare_input = compare_input.transpose((2, 0, 1))
    result = reid_exec_net.infer(inputs={reid_input_name: compare_input})
    compare_feature = result[reid_output_name]

    if not os.path.exists(feature_folder_path):
        print("Feature folder path does not exist")
        return
    
    if not os.path.exists(gallery_folder_path):
        print("Gallery folder path does not exist")
        return

    feature_list = os.listdir(feature_folder_path)
    gallery_list = os.listdir(gallery_folder_path)

    if feature_list is None:
        print("Feature folder is empty")
        return
    
    if gallery_list is None:
        print("Gallery folder is empty")
        return
    
    if len(feature_list) != len(gallery_list):
        print("Feature folder and Gallery folder do not have same number of files")
        return

    if not os.path.exists("results"):
        os.makedirs("results")

    pbar = tqdm.tqdm(total=len(feature_list), desc="Searching")
    for feature in feature_list:
        pbar.update(1)
        feature_path = os.path.join(feature_folder_path, feature)
        feature = np.load(feature_path)
        similarity = cosine_similarity(feature, compare_feature)
        if similarity > threshold:
            filename = feature_path.split('/')[-1].split('.')[0]
            image_path = gallery_folder_path + '/' + filename + '.png'
            image = cv2.imread(image_path)
            #filename should contain video name, frame number, and detection number
            cv2.imwrite("results/" + filename + ".png", image)
    pbar.close()


def createClusters(feature_folder_path, gallery_folder_path, cluster_size=10):
    #create clusters of all detections in the gallery

    if not os.path.exists(feature_folder_path):
        print("Feature folder path does not exist")
        return
    
    if not os.path.exists(gallery_folder_path):
        print("Gallery folder path does not exist")
        return

    feature_list = os.listdir(feature_folder_path)
    gallery_list = os.listdir(gallery_folder_path)

    if feature_list is None:
        print("Feature folder is empty")
        return
    
    if gallery_list is None:
        print("Gallery folder is empty")
        return
    
    if len(feature_list) != len(gallery_list):
        print("Feature folder and Gallery folder do not have same number of files")
        return
    
    if not os.path.exists("clusters"):
        os.makedirs("clusters")

    features = []
    for feature in feature_list:
        feature_path = os.path.join(feature_folder_path, feature)
        feature = np.load(feature_path)
        features.append(feature)
    
    features = np.array(features)
    features = features.reshape(features.shape[0], features.shape[2])
    kmeans = KMeans(n_clusters=cluster_size, random_state=0, n_init=10).fit(features)
    #for all detections in the gallery, save the cluster number in a folder
    for i in range(len(kmeans.labels_)):
        filename = feature_list[i].split('.')[0]
        image_path = gallery_folder_path + '/' + filename + '.png'
        image = cv2.imread(image_path)
        if not os.path.exists("clusters/" + str(kmeans.labels_[i])):
            os.makedirs("clusters/" + str(kmeans.labels_[i]))
        cv2.imwrite("clusters/" + str(kmeans.labels_[i]) + "/" + filename + ".png", image)


def searchQuery(compare_image_path, video_folder_path, threshold=0.5):

    if not os.path.exists(compare_image_path):
        print("Search image path does not exist")
        return

    compare_input = cv2.imread(compare_image_path)
    compare_input = cv2.resize(compare_input, (128, 256))
    compare_input = compare_input.transpose((2, 0, 1))
    result = reid_exec_net.infer(inputs={reid_input_name: compare_input})
    compare_feature = result[reid_output_name]

    #for all videos in the database
    #for all frames in the video
    #for all detections in the frame
    #get the feature of the detection
    #compare the feature of the detection with the feature of the query
    #if the similarity is greater than a threshold, then cropped the detection and save it in a folder

    if not os.path.exists(video_folder_path):
        print("Video folder path does not exist")
        return

    video_list = os.listdir(video_folder_path)

    if video_list is None:
        print("Video folder is empty")
        return
    
    if not os.path.exists("results"):
        os.makedirs("results")

    for video in video_list:
        video_path = os.path.join(video_folder_path, video)
        cap = cv2.VideoCapture(video_path)
        pbar = tqdm.tqdm(total=cap.get(cv2.CAP_PROP_FRAME_COUNT), desc=video)
        while True:
            ret, frame = cap.read()
            pbar.update(1)
            if not ret:
                break
            if ret and frame is not None and frame.size!=0:
                input_data = cv2.resize(frame, (544, 320))
                input_data = input_data.transpose((2, 0, 1))
                result = det_exec_net.infer(inputs={det_input_name: input_data})
                output = result[det_output_name]

                for detection in output[0][0]:
                    confidence = detection[2]
                    if confidence > 0.5:
                        xmin = int(detection[3] * frame.shape[1])
                        ymin = int(detection[4] * frame.shape[0])
                        xmax = int(detection[5] * frame.shape[1])
                        ymax = int(detection[6] * frame.shape[0])
                        cropped = frame[ymin:ymax, xmin:xmax]
                        if cropped.size == 0:
                            continue
                        cropped = cv2.resize(cropped, (128, 256))
                        cropped = cropped.transpose((2, 0, 1))
                        feature_result = reid_exec_net.infer(inputs={reid_input_name: cropped})
                        feature = feature_result[reid_output_name]
                        similarity = cosine_similarity(feature, compare_feature)
                        if similarity > threshold:
                            cv2.imwrite("results/" + video + "_" + str(int(cap.get(cv2.CAP_PROP_POS_FRAMES))) + "_" + str(uuid.uuid4()) + ".png", cropped.transpose((1, 2, 0)))
        pbar.close()                            
            



if __name__ == '__main__':
    detection_model_xml = "./models/person-detection-retail-0013/FP16/person-detection-retail-0013.xml"
    detection_model_bin = "./models/person-detection-retail-0013/FP16/person-detection-retail-0013.bin"
    reid_model_xml = "./models/person-reidentification-retail-0277/FP16/person-reidentification-retail-0277.xml"
    reid_model_bin = "./models/person-reidentification-retail-0277/FP16/person-reidentification-retail-0277.bin"

    ie = IECore()

    det_net = ie.read_network(model=detection_model_xml, weights=detection_model_bin)
    det_inputs = det_net.input_info
    det_input_name = next(iter(det_net.input_info))
    det_input_shape = det_inputs[det_input_name].input_data.shape
    det_outputs = det_net.outputs
    det_output_name = next(iter(det_net.outputs))
    det_exec_net = ie.load_network(network=det_net, device_name="CPU")

    reid_net = ie.read_network(model=reid_model_xml, weights=reid_model_bin)
    reid_inputs = reid_net.input_info
    reid_input_name = next(iter(reid_net.input_info))
    reid_input_shape = reid_inputs[reid_input_name].input_data.shape
    reid_outputs = reid_net.outputs
    reid_output_name = next(iter(reid_net.outputs))
    reid_exec_net = ie.load_network(network=reid_net, device_name="CPU")

    #Example usage
    #searchQuery("/Users/zain/Desktop/Screenshots/Screenshot 2023-06-16 at 7.25.22 AM.png", "/Users/zain/Desktop/PersonReID_Prototype/campus_videos")
    #saveFeatures("/Users/zain/Desktop/PersonReID_Prototype/campus_videos")
    #searchFeatures("/Users/zain/Desktop/Screenshots/Screenshot 2023-06-16 at 7.25.22 AM.png", "/Users/zain/Downloads/Person_ReID_Testing/features", "/Users/zain/Downloads/Person_ReID_Testing/gallery")
    #createClusters("/Users/zain/Downloads/Person_ReID_Testing/features", "/Users/zain/Downloads/Person_ReID_Testing/gallery", 10)