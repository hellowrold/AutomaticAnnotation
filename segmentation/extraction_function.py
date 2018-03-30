#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import random
import Image
from sklearn.cluster import MeanShift,KMeans

import apiclient
import random
import json
import time
import requests
import matlab.engine
from scipy import misc

appId="100161"
appKey="Bj0nLhCmATQWy0ZDXnsQf6MKgSM42y1mH97DxWDcdAI"
secretKey="okp5bmmJW85DO1U7lhr8gj23SxAtdP7Us-NV72yKtzs"

eng = matlab.engine.start_matlab()

def find_textRegion(text_lines,w,h):

    yAxis = []
    #偏移量的控制
    bias = 0.5
    
    for line in text_lines:
        yAxis.append(line[1])

    yAxis_copy = list(yAxis)
    yAxis_copy.sort(reverse=False)

    filter_lines = []
    lines_size = []
    for i in range(len(yAxis_copy)):
        index = yAxis.index(yAxis_copy[i])
        eachline = text_lines[index]
        lines_size.append((eachline[3]-eachline[1])*(eachline[2]-eachline[0]))

    maxh_index = lines_size.index(max(lines_size))
    filter_lines.append(text_lines[yAxis.index(yAxis_copy[maxh_index])])

    if maxh_index > 0 and maxh_index < len(yAxis_copy)-1:
        for i in reversed(range(1,maxh_index+1)):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            #判断二者中心点的偏移是否大于前一行宽度的X倍
            if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < bias*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.insert(0,eachline_prior)

        for i in range(maxh_index,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]

            if abs((eachline_next[0] + eachline_next[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < bias*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.append(eachline_next)
    
    elif maxh_index == 0:
        for i in range(0,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]
            #若相邻行间距大于前一行的X倍高度
            if abs((eachline_next[0] + eachline_next[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < bias*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.append(eachline_next)

    elif maxh_index == (len(yAxis_copy)-1):
        for i in reversed(range(1,len(yAxis_copy))):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < bias*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.insert(0,eachline_prior)
    
    #filter_lines中的文字已经按照从上到下的顺序排列
    filter_lines = np.array(filter_lines)

    boundingBox = [0.0,0.0,0.0,0.0]
    boundingBox[0] = filter_lines[0][0]
    boundingBox[1] = filter_lines[0][1]
    boundingBox[2] = filter_lines[0][2]
    boundingBox[3] = filter_lines[len(filter_lines)-1][3]

    for i in range(len(filter_lines)):
        eachline = filter_lines[i]
        boundingBox[0] = min(boundingBox[0],eachline[0])
        boundingBox[2] = max(boundingBox[2],eachline[2])

    currentW = boundingBox[2] - boundingBox[0]
    currentH = boundingBox[3] - boundingBox[1]

    if (boundingBox[0] - 0.25*currentW) > 0:
        boundingBox[0] = boundingBox[0] - 0.25*currentW

    if (boundingBox[2] + 0.25*currentW) < w:
        boundingBox[2] = boundingBox[2] + 0.25*currentW

    boundingBox[1] = 0.5*boundingBox[1]
    boundingBox[3] = boundingBox[3] + 0.5*(h-boundingBox[3])

    return filter_lines,boundingBox
    

def textlines_merge(text_lines):
    yAxis = []
    mergeRate = 0.35 #容错率阈值
    
    for line in text_lines:
        yAxis.append(line[1])

    yAxis_copy = list(yAxis)
    yAxis_copy.sort(reverse=False)

    if len(yAxis) > 0:
        filter_lines = []
        filter_lines.append(text_lines[yAxis.index(yAxis_copy[0])])

        for i in range(1,len(yAxis_copy)):

            index = yAxis.index(yAxis_copy[i])
            eachline = filter_lines[-1]
            eachline_next = text_lines[index]

            if overlap_degree(eachline,eachline_next) > mergeRate :
                #合并
                filter_lines[-1][0] = min(eachline[0],eachline_next[0])
                filter_lines[-1][1] = min(eachline[1],eachline_next[1])
                filter_lines[-1][2] = max(eachline[2],eachline_next[2])
                filter_lines[-1][3] = max(eachline[3],eachline_next[3])
            else:
                filter_lines.append(eachline_next)

        filter_lines = np.array(filter_lines)
        #print(filter_lines)
        return filter_lines
    else:
        return text_lines

                    
def filer_LittleText(text_lines):

    text_left = []
    for i in range (len(text_lines)):
        line = text_lines[i]
        if (line[2] - line[0]) > 10 and  (line[3] - line[1]) > 10:
            text_left.append(line)
    return text_left

def backgroundMask(w,h,text_difColor,text_lines,masks,className,prefix,suffix):
    backgroundMask = np.zeros((h,w))

    for m in range(len(className)):
        each = className[m]
        for i in range(len(masks)):
            productBoundary = each[0][i]
            mask = masks[i]
            for j in range(mask.shape[0]):
                for k in range(mask.shape[1]):
                    if mask[j][k]>0:
                        backgroundMask[int(productBoundary[1])+j][int(productBoundary[0])+k] = 255


    for each in text_difColor:
        for j in range(int(each[1]),int(each[3])):
            for k in range(int(each[0]),int(each[2])):
                backgroundMask[j][k] = 255

    for each in text_lines:
        for j in range(int(each[1]),int(each[3])):
            for k in range(int(each[0]),int(each[2])):
                backgroundMask[j][k] = 255

    misc.imsave('../productSegments/'+prefix+'_backgroundMask'+suffix, backgroundMask)

    return prefix+'_backgroundMask'+suffix


def overlap_degree(rect_current,rect_next):

    #deltaY = rect_current[3] - rect_next[1]
    #if deltaY > 0:

    if rect_current[1] < rect_next[3] and rect_current[3] > rect_next[1]:
        if rect_current[0] < rect_next[2] and rect_current[2] > rect_next[0]:
            #Y轴相交，X轴相交
            deltaX = min(rect_current[2],rect_next[2]) - max(rect_current[0],rect_next[0])
            deltaY = min(rect_current[3],rect_next[3]) - max(rect_current[1],rect_next[1])
            size_eachline = (rect_current[2]-rect_current[0])*(rect_current[3]-rect_current[1])
            size_nextline = (rect_next[2]-rect_next[0])*(rect_next[3]-rect_next[1])
            return deltaY*deltaX/min(size_eachline,size_nextline)
        else:
            #Y轴相交，X轴不交，求X轴上的距离
            Xdist = min(abs(rect_next[2] - rect_current[0]),abs(rect_next[0] - rect_current[2]))
            return -Xdist/min(rect_current[2]-rect_current[0],rect_next[2]-rect_next[0])
            
    else:
        if rect_current[0] < rect_next[2] and rect_current[2] > rect_next[0]:
            #Y轴不交，X轴交，求Y轴距离
            Ydist = min(abs(rect_next[3] - rect_current[1]),abs(rect_next[1] - rect_current[3]))
            return -Ydist/min(rect_current[3]-rect_current[1],rect_next[3]-rect_next[1])
            
        else:
            #Y轴不交，X轴不相交
            return -10

def text_segmentation(preffixName, suffixName, textNum, textLines):


    for i in range(textNum+1):

        imgName = preffixName+'_text'+ str(i)+suffixName

        tempImage = Image.open(imgName)
        w,h = tempImage.size
        ratio = max((50*1.0/w),(50*1.0/h))
        if ratio > 1:
            tw = int(w * ratio)  
            th = int(h * ratio)  
            tempImage = tempImage.resize((tw,th),Image.ANTIALIAS)
        else:
            ratio = 1
        tempImage.save('./temp.jpg')
        count, contents, location, num = text_recognition('./temp.jpg',ratio)

        boundary = [0,0,0,0] #边界存储顺序为左，上，右，下

        textImg = Image.open(imgName)
        textImg = textImg.convert('RGB')
        textImg = np.asarray(textImg)

        saliencyImg = Image.open(preffixName+'_saliency'+ str(i)+suffixName)
        saliencyImg = np.asarray(saliencyImg)

        textBack_color= textImg[saliencyImg<10]
        text_color = textImg[saliencyImg>220]


        backColor = np.mean(textBack_color,axis=0)
        textColor = np.mean(text_color,axis=0)
        textline = textLines[i]

        #左边
        for j in range(0,textImg.shape[1]):
            averageColor = []
            for k in range(0,textImg.shape[0]):
                if np.sqrt(np.sum(np.square(textColor - textImg[k][j]))) < 20:
                    averageColor.append(textImg[k][j]*10)
                averageColor.append(textImg[k][j])

            averageColor = np.asarray(averageColor)
            value = np.mean(averageColor,axis=0)
            dist = np.sqrt(np.sum(np.square(backColor - value)))
            
            if dist>20:
                boundary[0] = j
                break

        #上边
        for j in range(0,textImg.shape[0]):
            averageColor = []
            for k in range(0,textImg.shape[1]):
                if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                    averageColor.append(textImg[j][k]*10)
                averageColor.append(textImg[j][k])

            averageColor = np.asarray(averageColor)
            value = np.mean(averageColor,axis=0)
            dist = np.sqrt(np.sum(np.square(backColor - value)))

            if dist>14:
                boundary[1] = j
                break

        #右边
        for j in range(textImg.shape[1]-1,0,-1):

            averageColor = []
            for k in range(0,textImg.shape[0]):
                if np.sqrt(np.sum(np.square(textColor - textImg[k][j]))) < 20:
                    averageColor.append(textImg[k][j]*10)
                averageColor.append(textImg[k][j])


            averageColor = np.asarray(averageColor)
            value = np.mean(averageColor,axis=0)
            dist = np.sqrt(np.sum(np.square(backColor - value)))

            if dist>20:
                boundary[2] = j
                break


        #下边
        for j in range(textImg.shape[0]-1,0,-1):

            averageColor = []
            for k in range(0,textImg.shape[1]):
                if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                    averageColor.append(textImg[j][k]*10)
                averageColor.append(textImg[j][k])

            averageColor = np.asarray(averageColor)
            value = np.mean(averageColor,axis=0)
            dist = np.sqrt(np.sum(np.square(backColor - value)))

            if dist>14:
                boundary[3] = j
                break

        x = textLines[i][0]
        y = textLines[i][1]
        textLines[i][0] = (x + boundary[0])
        textLines[i][1] = (y + boundary[1])
        textLines[i][2] = (x + boundary[2])
        textLines[i][3] = (y + boundary[3])

    return textLines

def text_recognition(imgName,ratio):

    client = apiclient.OpenApiClient(appId,appKey,secretKey);

    fileParams = {"image":open(imgName, "rb")}
    params= {"appId":appId,"userId":"hello","groupName":"testxxx"}
    result = client.executePost("image/v1/wordrecognize",params,fileParams)
    aa = json.dumps(result,ensure_ascii=False)
    a = json.loads(aa)
    b = a['data']
    number = len(b)

    #接口有问题，先不提取文字
    #number = -1

    if number > 0:
        a = json.loads(json.dumps(b[0],ensure_ascii=False))
        contents = "".join(a['contents'])

        for i in range(1,len(b)):
            a = json.loads(json.dumps(b[i],ensure_ascii=False))
            contents = contents + ",".join(a['contents'])
        return contents,number
    else:
        return "",number

def color_analysis(preffixName, suffixName, textNum, textLines):

    textLinesLeft = []
    backColors = []
    maxSize = 0
    index_maxSize = 0
    for i in range(textNum+1):
        textImg = Image.open(preffixName+'text'+ str(i)+suffixName)
        textImg = textImg.convert('RGB')
        textImg = np.asarray(textImg)
        if (textImg.shape[0]*textImg.shape[1])>maxSize:
            maxSize = textImg.shape[0]*textImg.shape[1]
            index_maxSize = i

        saliencyImg = Image.open(preffixName+'saliency'+ str(i)+suffixName)
        saliencyImg = np.asarray(saliencyImg)

        textBack_color= textImg[saliencyImg<10]
        backColors.append(np.mean(textBack_color,axis=0))

        #尝试聚类处理
        #backColor = getMainColor(textBack_color,5)
        #backColors.append(backColor)       

    if len(backColors) > 0:
        backColors = np.array(backColors)

        #区分的阈值,该值可调整
        ms = MeanShift(bandwidth=50, bin_seeding=True)
        ms.fit(backColors)
        labels = ms.labels_
        cluster_centers = ms.cluster_centers_

        binCount = np.bincount(labels).tolist()

        Label_index = []
        for i in range (len(binCount)):
            eachLabel_index = []
            for j in range(len(labels)):
                if labels[j] == i:
                    eachLabel_index.append(j)
            Label_index.append(eachLabel_index)
        
        maxLabel = labels[index_maxSize]

        results = []

        for i in range(len(Label_index)):
            if i != maxLabel:
                texts_eachlabel = Label_index[i]
                if len(texts_eachlabel) > 1:
                    yAxis = []
                    for index in texts_eachlabel:
                        yAxis.append(textLines[index][1])

                    yAxis_copy = list(yAxis)
                    yAxis_copy.sort(reverse=False)

                    results.append(textLines[texts_eachlabel[yAxis.index(yAxis_copy[0])]])

                    for i in range(1,len(yAxis_copy)):

                        index = texts_eachlabel[yAxis.index(yAxis_copy[i])]
                        eachline = results[-1]
                        eachline_next = textLines[index]

                        if overlap_degree(eachline,eachline_next) > -1 :
                            #合并
                            results[-1][0] = min(eachline[0],eachline_next[0])
                            results[-1][1] = min(eachline[1],eachline_next[1])
                            results[-1][2] = max(eachline[2],eachline_next[2])
                            results[-1][3] = max(eachline[3],eachline_next[3])
                        else:
                            results.append(eachline_next)
                else:
                    results.append(textLines[texts_eachlabel[0]])
            else: 
                texts_eachlabel = Label_index[i]
                for index in texts_eachlabel:
                    textLinesLeft.append(textLines[index])

        return results,textLinesLeft
    else:
        return [],textLines


def product_merge(className):

    product_boundary = []
    mergeRate = 0 #合并阈值


    for each in className:
        for classBox in each[0]:
            product_boundary.append([classBox[0],classBox[1],classBox[2],classBox[3]])

    xAxis = []
    for boundary in product_boundary:
        xAxis.append(boundary[0])

    if len(xAxis) > 0:   
        xAxis_copy = list(xAxis)
        xAxis_copy.sort(reverse=False)

        filter_product = []
        filter_product.append(product_boundary[xAxis.index(xAxis_copy[0])])

        for i in range(1,len(xAxis_copy)):

            index = xAxis.index(xAxis_copy[i])
            eachline = filter_product[-1]
            eachline_next = product_boundary[index]

            if overlap_degree(eachline,eachline_next) > mergeRate :
                #合并
                filter_product[-1][0] = min(eachline[0],eachline_next[0])
                filter_product[-1][1] = min(eachline[1],eachline_next[1])
                filter_product[-1][2] = max(eachline[2],eachline_next[2])
                filter_product[-1][3] = max(eachline[3],eachline_next[3])
            else:
                filter_product.append(eachline_next)

        filter_product = np.array(filter_product)
        #print(filter_lines)
        return filter_product
    else:
        return product_boundary

def productJson(className,cutImages,masks,prefix,suffix):

    results = []
    normalizedMasks = []
    for m in range(len(className)):

        each = className[m]
        label = each[1]

        for i in range(len(masks)):
            product_boundary = each[0][i]
            mask = masks[i]
            normalizedMask = np.zeros((mask.shape[0],mask.shape[1]))
            for j in range(mask.shape[0]):
                for k in range(mask.shape[1]):
                    if mask[j][k][0] > 0:
                        normalizedMask[j][k] = 255
            normalizedMasks.append(normalizedMask)
            misc.imsave('../productSegments/'+prefix+'_mask_'+label+str(i)+suffix, normalizedMask)
        
        for i in range(len(masks)):
            jsonResult = {}
            classBox = each[0][i]
            width = classBox[2] -classBox[0]
            height = classBox[3] -classBox[1]
            jsonResult['label'] = label
            jsonResult['x'] = classBox[0]
            jsonResult['y'] = classBox[1]
            jsonResult['width'] = width
            jsonResult['height'] = height
            jsonResult['mask'] = prefix+'_product'+str(i)+suffix
            results.append(jsonResult)

    return results,normalizedMasks

def textJson(text_difColor,text_lines,input_path):

    results = []
    inputImage = Image.open(input_path)
    
    for i in range(len(text_difColor)):
        jsonResult = {}
        line = text_difColor[i]
        box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
        textSegment = inputImage.crop((box[0],box[1], box[2], box[3]))

        w,h = textSegment.size
        ratio = max((50*1.0/w),(50*1.0/h))
        if ratio > 1:
            tw = int(w * ratio)  
            th = int(h * ratio)  
            textSegment = textSegment.resize((tw,th),Image.ANTIALIAS)
        else:
            ratio = 1
        textSegment.save('./temp.jpg')
        contents, num = text_recognition('./temp.jpg',ratio)

        eng.GetMC('./temp.jpg','./tempSaliency.jpg')
        saliencyImg = Image.open('./tempSaliency.jpg')

        textSegment = np.array(textSegment)
        saliencyImg = np.asarray(saliencyImg)
        textBack_color= textSegment[saliencyImg<10]
        colorBackgroud = np.mean(textBack_color,axis=0)
        #colorBackgroud = colorBackgroud.tolist()
        colorBackgroud = str(int(colorBackgroud[0])) +','+ str(int(colorBackgroud[1])) +','+ str(int(colorBackgroud[2]))

        text_color = textSegment[saliencyImg>220]
        colorText = np.mean(text_color,axis=0)
        #colorText = colorText.tolist()
        colorText = str(int(colorText[0])) + ',' + str(int(colorText[1])) + ','+  str(int(colorText[2]))

        jsonResult['label'] = "highlight" #强调的内容
        jsonResult['x'] = box[0]
        jsonResult['y'] = box[1]
        jsonResult['width'] = box[2]-box[0]
        jsonResult['height'] = box[3]-box[1]
        jsonResult['contents'] = contents
        jsonResult['textColor'] = colorText
        jsonResult['backColor'] = colorBackgroud

        results.append(jsonResult)

    for i in range(len(text_lines)):
        jsonResult = {}
        line = text_lines[i]
        box = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
        textSegment = inputImage.crop((box[0],box[1], box[2], box[3]))

        w,h = textSegment.size
        ratio = max((50*1.0/w),(50*1.0/h))
        if ratio > 1:
            tw = int(w * ratio)  
            th = int(h * ratio)  
            textSegment = textSegment.resize((tw,th),Image.ANTIALIAS)
        else:
            ratio = 1
        textSegment.save('./temp.jpg')
        contents, num = text_recognition('./temp.jpg',ratio)

        eng.GetMC('./temp.jpg','./tempSaliency.jpg')
        saliencyImg = Image.open('./tempSaliency.jpg')

        textSegment = np.array(textSegment)
        saliencyImg = np.asarray(saliencyImg)
        textBack_color= textSegment[saliencyImg<10]
        colorBackgroud = np.mean(textBack_color,axis=0)
        #colorBackgroud = colorBackgroud.tolist()
        colorBackgroud = str(int(colorBackgroud[0])) +','+ str(int(colorBackgroud[1])) +','+ str(int(colorBackgroud[2]))

        text_color = textSegment[saliencyImg>220]
        colorText = np.mean(text_color,axis=0)
        #colorText = colorText.tolist()
        colorText = str(int(colorText[0])) + ',' + str(int(colorText[1])) + ','+  str(int(colorText[2]))

        jsonResult['label'] = "formal" #强调的内容
        jsonResult['x'] = box[0]
        jsonResult['y'] = box[1]
        jsonResult['width'] = box[2]-box[0]
        jsonResult['height'] = box[3]-box[1]
        jsonResult['contents'] = contents
        jsonResult['textColor'] = colorText
        jsonResult['backColor'] = colorBackgroud

        results.append(jsonResult)

    return results