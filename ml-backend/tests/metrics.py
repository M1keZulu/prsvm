import openvino as ov
import numpy as np
import logging
import sys
import os
import cv2
import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import json

def main():
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'model.onnx')
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    features_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'features')
    logging.info("Model path: " + model_path)
    logging.info("Data path: " + data_path)
    logging.info("Features path: " + features_path)


    for file in os.listdir(data_path + '/query/'):
        if not file.endswith('.jpg') and not file.endswith('.png') and not file.endswith('.jpeg'):
            continue
        os.rename(data_path + '/query/' + file, data_path + '/gallery/' + file.split('.')[0] + '_query.jpg')

    core = ov.Core()
    devices = core.get_available_devices()
    logging.info("Available devices: " + str(devices))

    model = core.read_model(model_path)
    logging.info("Model loaded")

    compiled_model = core.compile_model(model, "CPU")
    logging.info("Model compiled")

    if not os.path.exists(features_path):
        os.makedirs(features_path)

    #extract features from images
    for folder in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, folder)):
            if not os.path.exists(os.path.join(features_path, folder)):
                os.makedirs(os.path.join(features_path, folder))
            pbar = tqdm.tqdm(total=len(os.listdir(os.path.join(data_path, folder))), desc=folder)
            for file in os.listdir(os.path.join(data_path, folder)):
                if not file.endswith('.jpg') and not file.endswith('.png') and not file.endswith('.jpeg'):
                    continue
                image_path = os.path.join(data_path, folder, file)
                image = cv2.imread(image_path)
                image = cv2.resize(image, (128, 256))
                image = image.transpose((2, 0, 1))
                image = np.expand_dims(image, axis=0)
                image = image.astype(np.float32)
                infer_request = compiled_model.create_infer_request()
                input_tensor = ov.Tensor(array=image)
                infer_request.set_input_tensor(input_tensor)
                infer_request.infer()
                output = infer_request.get_output_tensor()
                output_data = output.data
                assert output_data.dtype == np.float32
                np.save(os.path.join(features_path, folder, file.split('.')[0] + '.npy'), output_data)
                pbar.update(1)
            pbar.close()

    features = []
    labels = []
    name = []
    for file in os.listdir(features_path):
        if file not in ['gallery', 'query']:
            continue
        for feature in os.listdir(os.path.join(features_path, file)):
            features.append(np.load(os.path.join(features_path, file, feature)))
            labels.append(feature.split('_')[0])
            name.append(feature.split('.')[0])

    features = np.array(features)
    labels = np.array(labels)
    name = np.array(name)
    features = features.reshape(features.shape[0], -1)
    similarity = cosine_similarity(features, features)

    rank_1_acc = 0
    rank_5_acc = 0
    rank_10_acc = 0
    mean_average_precision = 0
    queries = 0

    #2 random nums in list where query in features
    random_nums = np.random.choice(np.where(np.char.endswith(name, 'query'))[0], 2, replace=False)
    random_nums = random_nums.tolist()

    for feature in range(len(features)):
        if "query" not in name[feature]:
            continue
        queries += 1
        q_pid = name[feature].split('_')[0]
        q_camid = name[feature].split('_')[1]

        rank = np.argsort(similarity[feature])[::-1]

        #remove all query suffix images from rank
        keep = np.invert(np.char.endswith(name[rank], 'query'))
        rank = rank[keep]

        #remove all images with same pid and camid from rank
        keep = np.invert(np.char.startswith(name[rank], q_pid + '_' + q_camid))
        rank = rank[keep]

        if feature in random_nums:
            #plot original image and top 10 similar images
            plt.figure(figsize=(20, 10))
            plt.subplot(1, 11, 1)
            plt.imshow(cv2.cvtColor(cv2.imread(os.path.join(data_path + "/gallery/", name[feature] + '.jpg')), cv2.COLOR_BGR2RGB))
            plt.title("Query")
            print("Query: " + name[feature] + " Label: " + labels[feature])
            plt.axis('off')
            for i in range(10):
                plt.subplot(1, 11, i+2)
                plt.imshow(cv2.cvtColor(cv2.imread(os.path.join(data_path + "/gallery/" , name[rank[i]] + '.jpg')), cv2.COLOR_BGR2RGB))
                plt.axis('off')
                print("Rank " + str(i+1) + ": " + name[rank[i]] + " Label: " + labels[rank[i]])
                #color the correct rank
                if labels[feature] == labels[rank[i]]:
                    plt.title("Rank " + str(i+1), color='green')
                else:
                    plt.title("Rank " + str(i+1), color='red')
            plt.savefig('example_' + str(random_nums.index(feature)) + '.jpg')

        #calculate rank 1, 5, 10 accuracy
        rank_1 = rank[0:1]
        rank_5 = rank[0:5]
        rank_10 = rank[0:10]
        if labels[feature] in labels[rank_1]:
            rank_1_acc += 1
        if labels[feature] in labels[rank_5]:
            rank_5_acc += 1
        if labels[feature] in labels[rank_10]:
            rank_10_acc += 1

        #calculate ap
        ap = 0
        correct = 0
        for i in range(len(rank)):
            if labels[rank[i]] == labels[feature]:
                correct += 1
                ap += correct / (i+1)
        if correct == 0:
            continue
        ap /= correct
        mean_average_precision += ap

    logging.info("Rank 1 accuracy: " + str(rank_1_acc/queries*100) + "%")
    logging.info("Rank 5 accuracy: " + str(rank_5_acc/queries*100) + "%")
    logging.info("Rank 10 accuracy: " + str(rank_10_acc/queries*100) + "%")
    logging.info("Mean average precision: " + str(mean_average_precision/queries*100) + "%")

    #dump results to metrics.json
    with open('metrics.json', 'w') as f:
        json.dump({"rank_1": rank_1_acc/queries*100, "rank_5": rank_5_acc/queries*100, "rank_10": rank_10_acc/queries*100, "map": mean_average_precision/queries*100}, f)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main()
