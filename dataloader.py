# -*- coding: utf-8 -*-
"""DataLoader.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FG0PHFW_d_QU3rOFgx-TxoSl7HoXLgfp

# Preamble
"""

import numpy as np
import rasterio
from typing import Sequence, Optional, Callable, Any
from torch.utils.data import Dataset, DataLoader
import os
from sklearn.model_selection import KFold
from torchvision.transforms import ToTensor
import glob
import rasterio
import json
from tqdm import tqdm
from skimage import io
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.plot import show,show_hist

jsonpath2 = '/content/drive/MyDrive/CropClassification/Data/Train/train_source_s2/ref_south_africa_crops_competition_v1_train_source_s2/collection.json'
labeljsonpath2 = '/content/drive/MyDrive/CropClassification/Data/Train/train_labels/ref_south_africa_crops_competition_v1_train_labels/collection.json'
bands_curr2=['B01','B02','B03','B04','B05','B06','B07','B08','B8A','B09','B11','B12','labels','field_ids']

"""# Band helper functions"""

def proportion_cloud(path_picture):
    img = io.imread(path_picture)
    prop_cloud = img.sum()/(256*256*255)  
    return(prop_cloud)

"""# Create bands dictionary"""

def get_Dict_data(path_to_collection,req_bands, size_subsample, max_prop_clm, check_clouds=False):
    #Args
    #> path to collection.Json
    #> which bands? - List of strings e.g. ['B02']
    #> subsample size - int < total pictures
    #> maximum proportion of clouded area in picture - float 0.-1.    
    
    ### open JSON
    
    # path to collection.JSON
    path_collection_Json = path_to_collection
    
    # open collection.JSON
    with open(path_collection_Json) as json_file_paths:
        alldat_Json = json.load(json_file_paths)
    
    # test data path  
    fold_path = path_collection_Json[0:-16]
    
    # list of individual stack.JSON/ select subset
    spec_dat = [fold_path + '/' + i['href'] for i in alldat_Json['links'][0:size_subsample]]
    
    ### get collection of individuals band links and put into list/dict
    dict_of_dict = {}
    l_of_dict = []
    
    ## for each folder
    for link in tqdm(spec_dat):
        #check if folder exists, elso do none
        try:
            # if exist, open individual stack.JSON
            with open(link) as json_file_paths_stack:
                curr_folder = json.load(json_file_paths_stack)['assets']
                
                # collect/generate links to specific band .tiff files
                band_path = {}
                for indx_D in curr_folder.keys():
                    band_path[indx_D] = link[0:-9] + curr_folder[indx_D]['href']
                
                # check cloud cover
                if check_clouds:
                  prop_clm = proportion_cloud(band_path['CLM'])
                  if (prop_clm <max_prop_clm): 
                    l_of_dict.append(band_path)
                  else:
                    None
                else:
                  l_of_dict.append(band_path)

    
                ## dict with unique location values 
                # date not considered !!!
                item = link.split('_')[-4]
                dict_of_dict[item] = curr_folder
        except:
            None
    
    dict_out = {}
    
    for band in req_bands:
        curr_band = [i[band] for i in l_of_dict]
        dict_out[band] = curr_band
    
    return dict_out


"""# Create bands + label dictionary"""

def get_file_list(data_json, label_json, req_bands, size_subsample, max_prop_clm, check_clouds=False, check_files=True):# path_to_collection,req_bands, size_subsample, max_prop_clm, check_clouds=False):
    #Args
    #> path to collection.Json
    #> which bands? - List of strings e.g. ['B02']
    #> subsample size - int < total pictures
    #> maximum proportion of clouded area in picture - float 0.-1.    
    
    ### open JSON  

    # open collection.JSON
    with open(data_json) as json_file_paths:
        alldat_Json = json.load(json_file_paths)
    with open(label_json) as json_file_paths:
      labeldat_Json = json.load(json_file_paths)


    # test data path  
    data_dir = data_json[0:-16]
    label_dir = os.path.dirname(label_json)

    # list of individual stack.JSON/ select subset
    spec_dat_tifs = [data_dir + '/' + i['href'] for i in alldat_Json['links']]
    spec_label_tifs = []
    for tif_dir in spec_dat_tifs:
      spec_label_tifs.append(label_dir + '/' + label_dir.split('/')[-1] + '_' + tif_dir.split('_')[-4] + '/stac.json')


    if check_files:
      # check the label file exsists:
      current_size = 0
      i = 0
      existing_label_tifs = []
      existing_dat_tifs = []
      while (current_size < size_subsample):
        if os.path.exists(spec_label_tifs[i]) and os.path.exists(spec_dat_tifs[i]):
          existing_label_tifs.append(spec_label_tifs[i])
          existing_dat_tifs.append(spec_dat_tifs[i])
          current_size += 1
        i += 1
    else:
      spec_dat_tifs = spec_dat_tifs[:size_subsample]
      spec_label_tifs = spec_label_tifs[:size_subsample]
    
    ### get collection of individuals band links and put into list/dict
    dict_of_dict = {}
    l_of_dict = []

    ## for each folder
    for label, dat in tqdm(zip(existing_label_tifs, existing_dat_tifs),total=len(existing_label_tifs)):
        #check if folder exists, elso do none
            # if exist, open individual stack.JSON
      
      # save the satelite tif paths
      with open(dat) as json_file_paths_stack:
        curr_folder = json.load(json_file_paths_stack)['assets']
      
      # collect/generate links to specific band .tiff files
      band_path = {}
      for indx_D in curr_folder.keys():
          band_path[indx_D] = dat[0:-9] + curr_folder[indx_D]['href']
      
      ## dict with unique location values 
      # date not considered !!!
      #item = link.split('_')[-4]
      #dict_of_dict[item] = curr_folder

      # save the label paths
      with open(label) as json_label_paths_stack:
        curr_folder = json.load(json_label_paths_stack)['assets']

      # collect/generate links to specific band .tiff files
      for indx_D in curr_folder.keys():
          band_path[indx_D] = os.path.join(os.path.dirname(label), curr_folder[indx_D]['href'])

      # check the cloud cover.
      if check_clouds:
        prop_clm = proportion_cloud(band_path['CLM'])
        if (prop_clm <max_prop_clm): 
          l_of_dict.append(band_path)
        else:
          None
      else:
        l_of_dict.append(band_path)

    dict_out = {}
    for band in req_bands:
        curr_band = [i[band] for i in l_of_dict]
        dict_out[band] = curr_band

    return dict_out


class Dataset_multiS2_T1(Dataset):#, Randomizable):
    def __init__(self, data_dict, im_transform, lbl_transform):
      self.label_file_list=data_dict['labels']
      self.s2_file_list=[data_dict[i] for i in data_dict.keys() if i not in ['labels','field_ids'] ]
      self.loader = rasterio.open
      self._seed = 0  # transform synchronization seed
      self.image_transform = im_transform
      self.label_transform = lbl_transform

    def __len__(self):
      return len(self.s2_file_list[0])
      # return len(self.label_directories) if we want just the number of areas mapped

    def randomize(self, data = None):
      self._seed = 2021 #self.R.randint(np.iinfo(np.int32).max)

    def make_label_images(self, img, n_classes):
      img = img.read().squeeze()
      img_shape = img.shape
      label_images = np.zeros(img_shape + (n_classes,))

      # find the labels in the input image
      vals = np.arange(n_classes)

      for i in vals:
        label_idx = np.where(img==i)
        label_images[label_idx[0], label_idx[1], i] = 1

      return label_images

    def make_image_images(self, file_list, index):
      image_images = np.zeros(self.loader(file_list[0][0]).read().squeeze().shape + (len(file_list),))

      for i in np.arange(len(file_list)):
        image_images[:,:,i] = self.loader(file_list[i][index]).read().squeeze()

      return image_images

    def __getitem__(self, index):
      self.randomize()
      #print(index)
      img_images = self.make_image_images(self.s2_file_list, index)
      

      lbl = self.loader(self.label_file_list[index])
      lbl_images = self.make_label_images(lbl, 10)
      #print(lbl_images.shape)
      return self.image_transform(img_images), self.label_transform(lbl_images)


def generate_splits(data_dict, split_ratios, shuffle=False):
  bands = list(data_dict.keys())
  kf = KFold(n_splits=split_ratios, shuffle=shuffle)
  train_files = list()
  test_files = list()
  
  for train_idx, test_idx in kf.split(range(len(data_dict[bands[0]]))):
    train_current_ims = {}
    test_current_ims = {}
    for band in bands:
      train_current_ims[band] = list()
      test_current_ims[band] = list()

    [[train_current_ims[key].append(data_dict[key][idx]) for idx in train_idx] for key in bands]
    train_files.append(train_current_ims)
    [[test_current_ims[key].append(data_dict[key][idx]) for idx in test_idx] for key in bands]
    test_files.append(test_current_ims)

  return train_files, test_files
