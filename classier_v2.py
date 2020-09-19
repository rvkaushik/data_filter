from PIL import Image
import numpy as np
import tensorflow as tf
import pathlib
from collections import Counter
import sqlite3
import os

def load_model(model_name):
    """
    Load a tensorflow model and return.
    param: model_name
    return: model
    """
    base_url = 'http://download.tensorflow.org/models/object_detection/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(
    fname=model_name,
    origin=base_url + model_file,
    untar=True)

    model_dir = pathlib.Path(model_dir)/"saved_model"

    model = tf.saved_model.load(str(model_dir))
    model = model.signatures['serving_default']

    return model

def run_inference_for_single_image(model, image):
    """
    Take a model and image for prediction and return dict of detections.
    """
    image = np.asarray(image)
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections
    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    return output_dict

def labels_map():
    labels = {
        "1": "person",
        "2": "bicycle",
        "3": "car",
        "4": "motorcycle",
        "8": "truck",
        "10": "traffic light",
        "18": "dog"
    }
    return labels

def filter_images(images_paths):
    paths, objects, images = [], [], []
    required_data = {}
    for path in images_paths:
        print(path)
        image = np.array(Image.open(path))
        output_dict = run_inference_for_single_image(model, image)
        print(list(zip(output_dict['detection_classes'], output_dict['detection_scores'])))
    return required_data

def create_insert_in_db(data):
    conn = sqlite3.connect("test_v2.db")
    try:
        CREATE_COMMAND = '''CREATE TABLE CLASSIFICATION
                            (ID INTEGER PRIMARY KEY,
                            FILEPATH    TEXT    NOT NULL,
                            CLS INT,
                            SCORE REAL);'''
        conn.execute(CREATE_COMMAND)
    except:
        print("TABLE ALREADY EXISTING")
    insert_querry = '''INSERT INTO CLASSIFICATION (FILEPATH, CLS,SCORE) VALUES (?, ?, ?)'''
    conn.executemany(insert_querry, data)
    conn.commit()
    print("CLOSING DB")
    conn.close()
    print("DONE")



if __name__ == '__main__':
    model = load_model("ssd_mobilenet_v1_coco_2017_11_17")
    image_folder_path = "/home/uar8kor/pdca/data_filtering/data/"
    image_path = []
    for root, sub, files in os.walk(image_folder_path):
        for f in files:
            image_path.append(os.path.join(root, f))
    data = filter_images(image_path)
   # create_insert_in_db(data)