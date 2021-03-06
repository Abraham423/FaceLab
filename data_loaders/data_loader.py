# -*- coding: utf-8 -*-
"""========================
@Project -> File : projects -> data_loader.py
@Date : Created on 2020/4/21 9:53
@author: wanghao
========================"""
import sys
import os
import torch.utils.data as data
import numpy as np
import cv2
from scipy import misc
from numpy.random import randint, shuffle, choice
from PIL import Image
import torchvision.transforms as transforms
import torch
import pickle as pkl
from sklearn.preprocessing import LabelEncoder
import torch.backends.cudnn as cudnn
sys.path.append("..")
from utils import concur_shuffle, get_all_images, generate_list

class Dataset(data.Dataset):
    def __init__(self,data_path=None, transform=None):
        self.data_path = data_path
        self.transform = transform
        if data_path.endswith("pkl"):
            data = pkl.load(open(data_path,"rb"))
            self.img_paths = data["img_paths"]
            self.labels = data["labels"]
        else:
            self.img_paths,_ = get_all_images(data_path)
            self.labels = self.get_label()
        self.num_classes = len(set(self.labels))
        self.img_paths,self.labels = concur_shuffle(self.img_paths,self.labels)
    def __getitem__(self,index):
        label = self.labels[index]
        img_path = self.img_paths[index]
        img = Image.open(img_path)
        if len(img.split()) != 3:
            img = img.convert("RGB")
        if self.transform is not None:
            try:
                img = self.transform(img)
            except Exception as e:
                print(e)
                import pdb;pdb.set_trace()
        return img, label
    def __len__(self):
        return len(self.img_paths)
    def get_label(self):
        dir_names = [x.split("/")[-2] for x in self.img_paths]
        label_encoder = LabelEncoder()
        labels = label_encoder.fit_transform(dir_names)
        return labels
        
class Data_Loader():
    def __init__(self,data_path=None,batch_size=64,p = 0.6,identity_size = 3,img_size=112,crop_size=100,
                rot_angle=10,num_workers=4,pin_memory=True,shuffle=True,**kwargs):
        self.data_path = data_path
        self.batch_size = batch_size
        self.p = p
        self.identity_size = identity_size
        self.img_size = img_size
        self.crop_size = crop_size
        self.rot_angle = rot_angle
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.shuffle = shuffle
        self.num_classes = None
        self.data_transform = transforms.Compose([
        transforms.Resize((img_size,img_size)),
        transforms.RandomRotation(rot_angle),
        transforms.RandomCrop(crop_size),
        transforms.Resize((img_size,img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
        ])
        # self.data_transform = transforms.Compose([
        #     transforms.RandomHorizontalFlip(),
        #     transforms.ToTensor(),
        #     transforms.Normalize(mean=[0.5, 0.5, 0.5],
        #                          std=[0.5, 0.5, 0.5])
        # ])
        self.build_dataset()
        self.build_loader()
    def reload(self):
        print("Rebuilding loader . . .")
        self.build_loader()
    def __len__(self):
        return self.sample_dataset.__len__()/self.batch_size
    def build_dataset(self):
        self.sample_dataset, self.num_calsses = get_train_dataset(self.data_path)
    def build_loader(self):
        self.sample_loader = torch.utils.data.DataLoader(dataset=self.sample_dataset,
                                                    batch_size=self.batch_size,
                                                    shuffle=self.shuffle,
                                                    pin_memory=self.pin_memory,
                                                    num_workers=self.num_workers,
                                                    )
                                                    



