#!/usr/bin/env python
# -*- coding: utf-8 -*-

from productPredict import productPredict
from textPredict import textPredict 
import os
import scipy.misc
import Image,ImageDraw
import extraction_function
import numpy as np
import simplejson as json

from lxml.etree import Element, SubElement, tostring
import pprint
from xml.dom.minidom import parseString

import matlab.engine

if __name__ == '__main__':

    eng = matlab.engine.start_matlab()
    
    #读取要处理的图片
    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo1/"
    imnames=os.listdir(DEMO_IMAGE_DIR)

    for name in imnames:

        input_path=DEMO_IMAGE_DIR+name
        print input_path
        inputImage = Image.open(input_path)
        inputImage = inputImage.convert('RGB')
        imgSize = np.asarray(inputImage)

        index = name.index('.')

        output_path = '../results/'+name[0:index] +'.xml'
        
        #-------------------识别图片中的产品（主要为人物）------------------------------
        predictImage,className,cutImages,masks = productPredict(input_path)
        scipy.misc.imsave('product.jpg', predictImage)
        #做一些合并
        product_boundary = extraction_function.product_merge(className)

        #-------------------识别图片中的字体（需二次识别）-------------------------
        text_lines,f = textPredict(input_path)
        if len(text_lines) > 0:
            '''           
            #切割图片，在做一次文字识别
            textRegion = inputImage.crop((boundingBox[0],boundingBox[1], boundingBox[2], boundingBox[3]))
            textRegion.save('textRegion.jpg')
            text_lines,f = textPredict('./textRegion.jpg')
            #最有可能的文字区域，

            for i in range(len(text_lines)):
                text_lines[i][0] = text_lines[i][0]/f + boundingBox[0]
                text_lines[i][1] = text_lines[i][1]/f + boundingBox[1]
                text_lines[i][2] = text_lines[i][2]/f + boundingBox[0]
                text_lines[i][3] = text_lines[i][3]/f + boundingBox[1]
            '''
            text_lines = text_lines/f
            #去掉过小
            text_lines = extraction_function.filer_LittleText(text_lines)
            #合并处理
            text_lines = extraction_function.textlines_merge(text_lines)

            '''
            #找到最有可能是文字的区域,去除其他文字
            text_lines,boundingBox = extraction_function.find_textRegion(text_lines,imgSize.shape[1],imgSize.shape[0])

            #得到文字片段及显著图
            for i in range (len(text_lines)):
                line = text_lines[i]
                box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])] 
                cropImage = inputImage.crop((box[0],box[1], box[2], box[3]))
                cropImage.save('../textResults/'+'text'+ str(i) + name[index:])
                eng.GetMC('../textResults/'+'text'+ str(i)+ name[index:],'../textResults/'+'saliency'+ str(i) + name[index:])

            i = len(text_lines)-1
            #字体边界refine
            #text_lines = extraction_function.text_segmentation('../textResults/'+name[0:index],name[index:], i,text_lines)
            #分析文字色彩，找到tag,action等信息
            text_difColor,text_lines = extraction_function.color_analysis('../textResults/',name[index:], i,text_lines)

            backgroundMask = extraction_function.backgroundMask(imgSize.shape[1],imgSize.shape[0],text_difColor,text_lines,masks,className,name[0:index],name[index:])
            '''

        node_root = Element('annotation')

        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'GTSDB'

        node_filename = SubElement(node_root, 'filename')
        node_filename.text = name

        node_size = SubElement(node_root, 'size')
        node_width = SubElement(node_size, 'width')
        node_width.text = str(imgSize.shape[1])

        node_height = SubElement(node_size, 'height')
        node_height.text = str(imgSize.shape[0])

        node_depth = SubElement(node_size, 'depth')
        node_depth.text = '3'

        for classBox in product_boundary:
            node_object = SubElement(node_root, 'object')
            node_name = SubElement(node_object, 'name')
            node_name.text = 'people'
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = str(int(classBox[0]))
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = str(int(classBox[1]))
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = str(int(classBox[2]))
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = str(int(classBox[3]))
        
        for i in range (len(text_lines)):
            line = text_lines[i]
            #if line[4] > 0.9:
            box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
            node_object = SubElement(node_root, 'object')
            node_name = SubElement(node_object, 'name')
            node_name.text = 'text'
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = str(box[0])
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = str(box[1])
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = str(box[2])
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = str(box[3])
        
        xml = tostring(node_root, pretty_print=True)  #格式化显示，该换行的换行
        dom = parseString(xml)


        xmlfile = open(output_path, 'w') 
        xmlfile.write(xml) 
        xmlfile.close()
        print xml



    file.close
        

