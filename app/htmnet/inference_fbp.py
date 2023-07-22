import os

import cv2
import numpy as np

import torch
import torch.nn as nn
import torchvision.transforms as transforms

from PIL import Image
from skimage import io
import dlib

from .hmtnet_fbp import HMTNet

predictor = dlib.shape_predictor(f'./models/shape_predictor_68_face_landmarks.dat')
detector = dlib.get_frontal_face_detector()
min_face_size = 88

model_path = f'./models/HMTNet.pth'


class HMTNetRecognizer:
    """
    HMTNet Recognizer Class Wrapper
    """

    def __init__(self, pretrained_model_path=model_path):
        model = HMTNet()
        model = model.float()
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)

        # model.load_state_dict(torch.load(pretrained_model_path))

        if torch.cuda.device_count() > 1:
            print("We are running on", torch.cuda.device_count(), "GPUs!")
            model = nn.DataParallel(model)
            model.load_state_dict(torch.load(pretrained_model_path))
        else:
            if torch.cuda.is_available():
                state_dict = torch.load(pretrained_model_path)
            else:
                state_dict = torch.load(pretrained_model_path, map_location=torch.device('cpu'))
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                name = k[7:]  # remove `module.`
                new_state_dict[name] = v
            model.load_state_dict(new_state_dict)

        model.to(device)
        model.eval()

        self.device = device
        self.model = model

    def infer(self, img_file):
        img = io.imread(img_file)
        img = Image.fromarray(img.astype(np.uint8))

        preprocess = transforms.Compose([
            transforms.Resize(227),
            transforms.RandomCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        img = preprocess(img)
        img.unsqueeze_(0)

        img = img.to(self.device)

        g_pred, r_pred, a_pred = self.model.forward(img)
        a_pred = a_pred.view(1, 1)

        return float(a_pred.cpu())


def mkdirs_if_not_exist(dir_name):
    """
    create new folder if not exist
    :param dir_name:
    :return:
    """
    if not os.path.isdir(dir_name) or not os.path.exists(dir_name):
        os.makedirs(dir_name)


def det_landmarks(image_path):
    """
    detect faces in one image, return face bbox and landmarks
    :param image_path:
    :return:
    """
    img = cv2.imread(image_path)
    faces = detector(img, 1)
    result = {}
    if len(faces) > 0:
        for k, d in enumerate(faces):
            shape = predictor(img, d)
            result[k] = {"bbox": [d.left(), d.top(), d.right(), d.bottom()],
                         "landmarks": [[shape.part(i).x, shape.part(i).y] for i in range(68)]}

    return result


def crop_face_from_image(image_path):
    dirname = os.path.dirname(image_path)
    crop_dir = dirname + '/crop/'
    file_name = os.path.basename(image_path)
    mkdirs_if_not_exist(crop_dir)

    res = det_landmarks(image_path)
    for i in range(len(res)):
        bbox = res[i]['bbox']
        for p in bbox:
            if p < 0:
                return None
        if bbox[3] - bbox[1] < min_face_size or bbox[2] - bbox[0] < min_face_size:  # Low res skip
            return None
        image = cv2.imread(image_path)
        face_region = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        output_path = os.path.join(crop_dir, file_name)
        cv2.imwrite(output_path, face_region)
        return output_path

    return None
