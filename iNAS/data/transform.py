import cv2
import numpy as np
import random
import torch

# salient object detection


class Resize(object):

    def __init__(self, base_size, image_only=False):
        self.h, self.w = base_size
        self.image_only = image_only

    def __call__(self, data_dict):
        image = data_dict['image']
        image = cv2.resize(image, (self.w, self.h), interpolation=cv2.INTER_LINEAR)
        data_dict['image'] = image

        if not self.image_only:
            label = data_dict['label']
            label = cv2.resize(label, (self.w, self.h), interpolation=cv2.INTER_NEAREST)
            data_dict['label'] = label

        return data_dict


class ToTensor(object):

    def __init__(self, mean=(0, 0, 0), std=(1., 1., 1.), image_only=False, label_normalize=True):
        self.mean = mean
        self.std = std
        self.image_only = image_only
        self.label_normalize = label_normalize

    def __call__(self, data_dict):
        image = data_dict['image']
        image = image.transpose(2, 0, 1).astype(np.float32)
        image = torch.from_numpy(image).div_(255)
        dtype, device = image.dtype, image.device
        mean = torch.as_tensor(self.mean, dtype=dtype, device=device)[:, None, None]
        std = torch.as_tensor(self.std, dtype=dtype, device=device)[:, None, None]
        image = image.sub(mean).div(std)
        data_dict['image'] = image

        if not self.image_only:
            label = data_dict['label']
            if self.label_normalize:
                label = torch.from_numpy((label / 255).astype(np.int64))  # 2-class sod 0/1
            else:
                label = torch.from_numpy(label.astype(np.int64))
            data_dict['label'] = label
        return data_dict


class RandomHorizontalFlip(object):

    def __init__(self, image_only=False):
        self.image_only = image_only

    def __call__(self, data_dict):
        if random.random() < 0.5:
            image = data_dict['image']
            image = cv2.flip(image, 1)
            data_dict['image'] = image
            if not self.image_only:
                label = data_dict['label']
                label = cv2.flip(label, 1)
                data_dict['label'] = label
        return data_dict


class Identity(object):

    def __call__(self, data_dict):
        return data_dict
