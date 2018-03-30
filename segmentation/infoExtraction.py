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

import matlab.engine

if __name__ == '__main__':

    eng = matlab.engine.start_matlab()
    '''
    #读取要处理的图片
    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo/"
    imnames=os.listdir(DEMO_IMAGE_DIR)
    '''

    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo1/"
    imnames=os.listdir(DEMO_IMAGE_DIR)

    '''
    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo/datatest/"
    file = open(DEMO_IMAGE_DIR+'test.html',"r")
    lines = file.readlines()[8:-4]
    num = len(lines)/7
    '''

    JsonData = []

    #for i in range(num):
    for name in imnames:
        '''
        name = lines[i*7+1][3:-5]
        describe = unicode(lines[i*7+5].strip('\n').strip('\r'), 'gbk')
        '''

        textsJson = []
        productsJson = []

        index = name.index('.')
        input_path=DEMO_IMAGE_DIR+name
        print input_path
        inputImage = Image.open(input_path)
        inputImage = inputImage.convert('RGB')
        imgSize = np.asarray(inputImage)

        #图片存放目录
        output_path = '../results/'+name[0:index] +'_result'+ name[index:]
        #文字存放目录
        text_output_path = '../results/'+name[0:index] +'_result'+ name[index:]
        
        #-------------------识别图片中的产品（主要为人物）------------------------------
        predictImage,className,cutImages,masks = productPredict(input_path)
        scipy.misc.imsave('product.jpg', predictImage)
        #保持原始数据的内容, 重新规范化了product的mask
        productsJson,masks= extraction_function.productJson(className,cutImages,masks,name[0:index],name[index:])
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
            #保持原始数据的内容
            textsJson = extraction_function.textJson(text_difColor,text_lines,input_path)

            backgroundMask = extraction_function.backgroundMask(imgSize.shape[1],imgSize.shape[0],text_difColor,text_lines,masks,className,name[0:index],name[index:])
            #json 格式封装输出
            outputData = {} #输出的字典

            outputData['name'] = name
            outputData['width'] = imgSize.shape[1]
            outputData['height'] = imgSize.shape[0]
            #outputData['BannerLabel'] = "clothing"
            outputData['backgroundMask'] = backgroundMask
            #outputData['description'] = describe
            outputData['texts'] = textsJson
            outputData['textsNum'] = len(textsJson)
            outputData['textRegionX'] = int(boundingBox[0])
            outputData['textRegionY'] = int(boundingBox[1])
            outputData['textRegionWidth'] = int(boundingBox[2]-boundingBox[0])
            outputData['textRegionHeight'] = int(boundingBox[3]-boundingBox[1])

            outputData['products'] = productsJson
            outputData['productsNum'] = len(productsJson)

            JsonData.append(outputData)
            #json_str = json.dumps(outputData)
            #print json_str

        #画图保存
        background = Image.open('product.jpg')
        background = background.convert('RGB')
        draw = ImageDraw.Draw(background)

        for classBox in product_boundary:
            draw.line([(classBox[0],classBox[1]),(classBox[2],classBox[1]),(classBox[2],classBox[3]),(classBox[0],classBox[3]),(classBox[0],classBox[1])], width=2, fill=(50,150,50,100))
        
        for i in range (len(text_lines)):
            line = text_lines[i]
            #if line[4] > 0.9:
            box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
            draw.line([(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3]),(box[0],box[1])], width=2, fill=(200,100,100,100))
        
        
        for i in range(len(text_difColor)):
            line = text_difColor[i]
            box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
            draw.line([(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3]),(box[0],box[1])], width=2, fill=(0,100,200,100))
            #draw.rectangle([box[0],box[1],box[2],box[3]],fill=(200,100,0,200))
    
        del draw
        background.save(output_path)

    json_str = json.dumps(JsonData)
    print json_str
    file.close
        

