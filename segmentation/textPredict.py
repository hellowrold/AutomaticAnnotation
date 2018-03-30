#!/usr/bin/env python
#
# The codes are used for implementing CTPN for scene text detection, described in:
#
# Z. Tian, W. Huang, T. He, P. He and Y. Qiao: Detecting Text in Natural Image with
# Connectionist Text Proposal Network, ECCV, 2016.
#
# Online demo is available at: textdet.com
#
# These demo codes (with our trained model) are for text-line detection (without
# side-refiement part).
#
#
# ====== Copyright by Zhi Tian, Weilin Huang, Tong He, Pan He and Yu Qiao==========

#            Email: zhi.tian@siat.ac.cn; wl.huang@siat.ac.cn
#
#   Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences
#
#

from cfg import Config as cfg
from other import draw_boxes, resize_im, CaffeModel
import cv2, os, caffe, sys
from detectors import TextProposalDetector, TextDetector
import os.path as osp
from utils.timer import Timer


def textPredict(input_path):

    #CPU mode setting
    if len(sys.argv)>1 and sys.argv[1]=="--no-gpu":
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(cfg.TEST_GPU_ID)

    model_path = "../models/"

    # initialize the detectors
    NET_DEF_FILE = model_path + "deploy.prototxt"
    MODEL_FILE = model_path + "ctpn_trained_model.caffemodel"

    text_proposals_detector=TextProposalDetector(CaffeModel(NET_DEF_FILE, MODEL_FILE))
    text_detector=TextDetector(text_proposals_detector)

    im=cv2.imread(input_path)
    #h = im.shape[0]
    #w = im.shape[1]
    im, f=resize_im(im, cfg.SCALE, cfg.MAX_SCALE)
    text_lines=text_detector.detect(im)

    return text_lines,f

    #im_with_text_lines=draw_boxes(im, text_lines, caption=im_name, wait=False

if __name__ == '__main__':
    textPredict('/home/learnCode/BannerSeg/demo/5-4.png')

