#!/usr/bin/env python
# -*- coding: utf-8 -*-

from productPredict import productPredict
from textPredict import textPredict 
import os
import scipy.misc
import Image,ImageDraw
import extraction_function
import numpy as np
import matlab.engine


if __name__ == '__main__':

    #图片输入的目录
    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo1/"
    imnames=os.listdir(DEMO_IMAGE_DIR)
    eng = matlab.engine.start_matlab()

    for name in imnames:

        index = name.index('.')
        input_path=DEMO_IMAGE_DIR+name
        output_path = '../results/'+name[0:index] +'_result'+ name[index:]

        inputImage = Image.open(input_path)
        inputImage = inputImage.convert('RGB')
        imgSize = np.asarray(inputImage)

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