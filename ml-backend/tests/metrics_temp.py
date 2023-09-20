import openvino as ov
import numpy as np
import logging
import sys
import os
import cv2
import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

def main():
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'model.onnx')
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    logging.info("Model path: " + model_path)
    logging.info("Data path: " + data_path)
    
    # core = ov.Core()
    # devices = core.get_available_devices()
    # logging.info("Available devices: " + str(devices))

    # model = core.read_model(model_path)
    # logging.info("Model loaded")

    # compiled_model = core.compile_model(model, "CPU")
    # logging.info("Model compiled")

    # if not os.path.exists('features'):
    #     os.makedirs('features')

    # for folder in os.listdir(data_path):
    #     if os.path.isdir(os.path.join(data_path, folder)):
    #         if not os.path.exists(os.path.join('features', folder)):
    #             os.makedirs(os.path.join('features', folder))
    #         pbar = tqdm.tqdm(total=len(os.listdir(os.path.join(data_path, folder))), desc=folder)
    #         for file in os.listdir(os.path.join(data_path, folder)):
    #             image_path = os.path.join(data_path, folder, file)
    #             image = cv2.imread(image_path)
    #             image = cv2.resize(image, (128, 256))
    #             image = image.transpose((2, 0, 1))
    #             image = np.expand_dims(image, axis=0)
    #             image = image.astype(np.float32)
    #             infer_request = compiled_model.create_infer_request()
    #             input_tensor = ov.Tensor(array=image)
    #             infer_request.set_input_tensor(input_tensor)
    #             infer_request.infer()
    #             output = infer_request.get_output_tensor()
    #             output_data = output.data
    #             assert output_data.dtype == np.float32
    #             np.save(os.path.join('features', folder, file.split('.')[0] + '.npy'), output_data)
    #             pbar.update(1)
    #         pbar.close()

    features = []
    labels = []
    name = []
    for folder in os.listdir('features'):
        for file in os.listdir(os.path.join('features', folder)):
            features.append(np.load(os.path.join('features', folder, file)))
            labels.append(folder)
            name.append(file.split('.')[0])
    for i in range(len(features)):
        features[i] = np.squeeze(features[i])
    features = np.array(features)
    labels = np.array(labels)
    
    similarity = cosine_similarity(features, features)

    rank_1_acc = 0
    rank_5_acc = 0
    rank_10_acc = 0
    queries = 0

    for feature in range(len(features)):
        if "query" not in name[feature]:
            continue
        queries += 1
        rank = np.argsort(similarity[feature])[::-1]

        # #plot original image and top 10 similar images
        # plt.figure(figsize=(20, 10))
        # plt.subplot(1, 11, 1)
        # plt.imshow(cv2.cvtColor(cv2.imread(os.path.join(data_path, labels[feature], name[feature] + '.png')), cv2.COLOR_BGR2RGB))
        # plt.title("Query")
        # plt.axis('off')
        # for i in range(10):
        #     plt.subplot(1, 11, i+2)
        #     plt.imshow(cv2.cvtColor(cv2.imread(os.path.join(data_path, labels[rank[i]], name[rank[i]] + '.png')), cv2.COLOR_BGR2RGB))
        #     plt.axis('off')
        #     #color the correct rank
        #     if labels[feature] == labels[rank[i]]:
        #         plt.title("Rank " + str(i+1), color='green')
        #     else:
        #         plt.title("Rank " + str(i+1), color='red')
        # plt.show()

        rank_1 = rank[1:2]
        rank_5 = rank[1:6]
        rank_10 = rank[1:11]
        if labels[feature] in labels[rank_1]:
            rank_1_acc += 1
        if labels[feature] in labels[rank_5]:
            rank_5_acc += 1
        if labels[feature] in labels[rank_10]:
            rank_10_acc += 1
    
    logging.info("Rank 1 accuracy: " + str(rank_1_acc/queries*100) + "%")
    logging.info("Rank 5 accuracy: " + str(rank_5_acc/queries*100) + "%")
    logging.info("Rank 10 accuracy: " + str(rank_10_acc/queries*100) + "%")

    # calculate mAP
    ap = []
    for feature in range(len(features)):
        if "query" not in name[feature]:
            continue
        rank = np.argsort(similarity[feature])[::-1]
        rank = rank[1:]
        ap.append(0)
        for i in range(len(rank)):
            if labels[feature] == labels[rank[i]]:
                ap[feature] += 1
        ap[feature] /= len(rank)
    ap = np.array(ap)
    mAP = np.mean(ap)
    logging.info("mAP: " + str(mAP*100) + "%")
    

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main()