#!/usr/bin/env python
# -*- coding: utf-8 -*-

from productPredict import productPredict
from textPredict import textPredict 
import postProcessing
import os
import scipy.misc
import Image,ImageDraw
import extraction_function
import numpy as np
from scipy import misc
import simplejson as json
import csv

from xml.dom.minidom import parse
import xml.dom.minidom

import matlab.engine


if __name__ == '__main__':

    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo1/"
    DEMO_XML_DIR = "/home/learnCode/BannerSeg/xml/"

    imnames=os.listdir(DEMO_XML_DIR)
    JsonData = []

    csvFile = open("/home/learnCode/BannerSeg/imgInfo.csv", "r")
    reader = csv.reader(csvFile)
    result = []
    for item in reader:
        # 忽略第一行
        eachline = {}
        eachline['name'] = item[0]
        eachline['describe'] = unicode(item[1],'gbk')
        eachline['category'] = unicode(item[2],'gbk')
        result.append(eachline)

    csvFile.close()

    for name in imnames:
        DOMTree = xml.dom.minidom.parse(DEMO_XML_DIR + name)

        collection  = DOMTree.documentElement

        fileNameTags = collection.getElementsByTagName("filename")
        folderTags = collection.getElementsByTagName("folder")
        objectTags = collection.getElementsByTagName("object")

        fileName = fileNameTags[0].childNodes[0].data

        folder = folderTags[0].childNodes[0].data

        jsonTexts = []
        product = []
        subbackground = []
        for index,objectTag in enumerate(objectTags):

            name  = objectTag.getElementsByTagName("name")[0].childNodes[0].data
            print name

            if (name == 'product'):
                location = []
                ptTags = objectTag.getElementsByTagName("pt")
                for ptTag in ptTags:
                    x = ptTag.getElementsByTagName("x")[0].childNodes[0].data
                    y = ptTag.getElementsByTagName("y")[0].childNodes[0].data
                    location.append((x,y))
                product.append(location)
            elif (name == 'subbackground'):

                location = []
                ptTags = objectTag.getElementsByTagName("pt")
                for ptTag in ptTags:
                    x = ptTag.getElementsByTagName("x")[0].childNodes[0].data
                    y = ptTag.getElementsByTagName("y")[0].childNodes[0].data
                    location.append((x,y))

                stratX = min(int(location[0][0]),int(location[1][0]),int(location[2][0]),int(location[3][0]))
                stratY = min(int(location[0][1]),int(location[1][1]),int(location[2][1]),int(location[3][1]))

                endX = max(int(location[0][0]),int(location[1][0]),int(location[2][0]),int(location[3][0]))
                endY = max(int(location[0][1]),int(location[1][1]),int(location[2][1]),int(location[3][1]))

                jsonResult = {}
                jsonResult['label'] = name #强调的内容
                jsonResult['x'] = stratX
                jsonResult['y'] = stratY
                jsonResult['width'] = endX - stratX
                jsonResult['height'] = endY - stratY

                subbackground.append(jsonResult)


            else:
                location = []
                ptTags = objectTag.getElementsByTagName("pt")
                for ptTag in ptTags:
                    x = ptTag.getElementsByTagName("x")[0].childNodes[0].data
                    y = ptTag.getElementsByTagName("y")[0].childNodes[0].data
                    location.append((x,y))

                stratX = min(int(location[0][0]),int(location[1][0]),int(location[2][0]),int(location[3][0]))
                stratY = min(int(location[0][1]),int(location[1][1]),int(location[2][1]),int(location[3][1]))

                endX = max(int(location[0][0]),int(location[1][0]),int(location[2][0]),int(location[3][0]))
                endY = max(int(location[0][1]),int(location[1][1]),int(location[2][1]),int(location[3][1]))

                jsonResult = {}
                jsonResult['label'] = name #强调的内容
                jsonResult['x'] = stratX
                jsonResult['y'] = stratY
                jsonResult['width'] = endX - stratX
                jsonResult['height'] = endY - stratY
                #jsonResult['contents'] = contents
                #jsonResult['textColor'] = colorText
                #jsonResult['backColor'] = colorBackgroud

                jsonTexts.append(jsonResult)

        



        index = fileName.index('.')
        input_path=DEMO_IMAGE_DIR+fileName
        output_path = '../results/'+fileName[0:index] +'_result'+ fileName[index:]

        text_output_path = '../results/'+fileName[0:index] +'_result'+ fileName[index:]

        inputImage = Image.open(input_path)
        inputImage = inputImage.convert('RGB')
        imgSize = np.asarray(inputImage)
        
        
        #产品处理
        predictImage,className,cutImages,masks = productPredict(input_path)
        #misc.imsave('../productSegments/'+fileName[0:index]+'_111'+fileName[index:], predictImage)

        normalizedMasks = []
        normalizedMask = np.zeros((imgSize.shape[0],imgSize.shape[1]))
        for k in range(len(className)):
            each = className[k]
            for i in range(len(masks)):
                product_boundary = each[0][i]
                cutImage = cutImages[i]
                mask = masks[i]
                for j in range(mask.shape[0]):
                    for k in range(mask.shape[1]):
                        if mask[j][k][0] > 0:
                            normalizedMask[j+int(product_boundary[1])][k+int(product_boundary[0])] = 255
            normalizedMasks.append(normalizedMask)
        misc.imsave('../productSegments/'+fileName[0:index]+'_mask'+fileName[index:], normalizedMask)
        
        
        jsonProducts = []
        for i in range(len(product)):
            each = product[i]

            stratX = min(int(each[0][0]),int(each[1][0]),int(each[2][0]),int(each[3][0]))
            stratY = min(int(each[0][1]),int(each[1][1]),int(each[2][1]),int(each[3][1]))

            endX = max(int(each[0][0]),int(each[1][0]),int(each[2][0]),int(each[3][0]))
            endY = max(int(each[0][1]),int(each[1][1]),int(each[2][1]),int(each[3][1]))

            maskImage = Image.open('../productSegments/'+fileName[0:index]+'_mask'+fileName[index:])
            boundaryImage = maskImage.crop((stratX,stratY,endX,endY))
            boundaryImage.save('../productSegments/'+fileName[0:index]+'_submask'+str(i)+fileName[index:])

            jsonResult = {}
            jsonResult['x'] = stratX
            jsonResult['y'] = stratY
            jsonResult['width'] = endX - stratX
            jsonResult['height'] = endY - stratY
            jsonResult['mask'] = fileName[0:index]+'_submask'+str(i)+fileName[index:]
            jsonProducts.append(jsonResult)



        info = result[int(fileName[0:index])]

        outputData = {} #输出的字典

        outputData['name'] = fileName
        outputData['description'] = info['describe']
        outputData['category'] = info['category']
        outputData['width'] = imgSize.shape[1]
        outputData['height'] = imgSize.shape[0]
        outputData['products'] = jsonProducts
        outputData['productsNum'] = len(jsonProducts)
        outputData['texts'] = jsonTexts
        outputData['textsNum'] = len(jsonTexts)
        outputData['subbackground'] = subbackground
        outputData['subbackgroundNum'] = len(subbackground)

        JsonData.append(outputData)

        
    json_str = json.dumps(JsonData)
    print json_str
        
        