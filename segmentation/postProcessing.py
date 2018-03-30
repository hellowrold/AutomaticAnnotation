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

appId="100161"
appKey="Bj0nLhCmATQWy0ZDXnsQf6MKgSM42y1mH97DxWDcdAI"
secretKey="okp5bmmJW85DO1U7lhr8gj23SxAtdP7Us-NV72yKtzs"

def textlines_yfilter(text_lines):

    yAxis = []
    yRate = 1.5 #y轴方向上的容错率阈值
    centerRate = 0.5 #x轴中心位置的容错率阈值
    
    for line in text_lines:
        yAxis.append(line[1])

    yAxis_copy = list(yAxis)
    yAxis_copy.sort(reverse=False)

    filter_lines = []
    lines_h = []
    for i in range(len(yAxis_copy)):
        index = yAxis.index(yAxis_copy[i])
        eachline = text_lines[index]
        lines_h.append(eachline[3]-eachline[1])

    #print(text_lines)
    #print(lines_h)
    maxh_index = lines_h.index(max(lines_h))
    #print(maxh_index)
    filter_lines.append(text_lines[yAxis.index(yAxis_copy[maxh_index])])

    if maxh_index > 0 and maxh_index < len(yAxis_copy)-1:
        for i in reversed(range(1,maxh_index+1)):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            #若相邻行间距大于小的X倍高度
            if ( eachline[1] - eachline_prior[3] ) > min((eachline_prior[3]-eachline_prior[1]),(eachline[3]-eachline[1]))*yRate:
                #判断二者中心点的偏移是否大于前一行宽度的X倍
                if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) > min((eachline_prior[2]-eachline_prior[0]),(text_lines[yAxis.index(yAxis_copy[maxh_index])][2]-text_lines[yAxis.index(yAxis_copy[maxh_index])][0]))*centerRate:
                    #为异常结果,以上都删除
                    print(eachline_prior)
                    break
                else:
                    filter_lines.insert(0,eachline_prior)
            else:
                filter_lines.insert(0,eachline_prior)

        for i in range(maxh_index,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]
            #若相邻行间距大于前一行的X倍高度
            if ( eachline_next[1] - eachline[3] ) > min((eachline[3]-eachline[1]),(eachline_next[3]-eachline_next[1]))*yRate:
                #判断二者中心点的偏移是否大于前一行宽度的X倍
                if abs((text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2 - (eachline_next[0] + eachline_next[2])/2) > min((text_lines[yAxis.index(yAxis_copy[maxh_index])][2]-text_lines[yAxis.index(yAxis_copy[maxh_index])][0]),(eachline_next[2]-eachline_next[0]))*centerRate:
                    #为异常结果
                    print(eachline_next)
                    break
                else:
                    filter_lines.append(eachline_next)
            else:
                filter_lines.append(eachline_next)
    elif maxh_index == 0:
        for i in range(0,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]
            #若相邻行间距大于前一行的X倍高度
            if ( eachline_next[1] - eachline[3] ) > min((eachline[3]-eachline[1]),(eachline_next[3]-eachline_next[1]))*yRate:
                #判断二者中心点的偏移是否大于前一行宽度的X倍
                if abs((text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2 - (eachline_next[0] + eachline_next[2])/2) > min((text_lines[yAxis.index(yAxis_copy[maxh_index])][2]-text_lines[yAxis.index(yAxis_copy[maxh_index])][0]),(eachline_next[2]-eachline_next[0]))*centerRate:
                    #为异常结果
                    print(eachline_next)
                    break
                else:
                    filter_lines.append(eachline_next)
            else:
                filter_lines.append(eachline_next)

    elif maxh_index == (len(yAxis_copy)-1):
        for i in reversed(range(1,len(yAxis_copy))):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            #若相邻行间距大于前一行的X倍高度
            if ( eachline[1] - eachline_prior[3] ) > min((eachline_prior[3]-eachline_prior[1]),(eachline[3]-eachline[1]))*yRate:
                #判断二者中心点的偏移是否大于前一行宽度的X倍
                if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) > min((eachline_prior[2]-eachline_prior[0]),(text_lines[yAxis.index(yAxis_copy[maxh_index])][2]-text_lines[yAxis.index(yAxis_copy[maxh_index])][0]))*centerRate:
                    #为异常结果,以上都删除
                    print(eachline_prior)
                    break
                else:
                    filter_lines.insert(0,eachline_prior)
            else:
                filter_lines.insert(0,eachline_prior)

    filter_lines = np.array(filter_lines)
    #print(filter_lines)
    return filter_lines

def textlines_xfilter(text_lines):

    xAxis = []
    xRate = 1 #y轴方向上的容错率阈值
    
    for line in text_lines:
        xAxis.append(line[0]+random.random())

    xAxis_copy = list(xAxis)
    xAxis_copy.sort(reverse=False)


    filter_lines = []
    lines_w = []
    for i in range(len(xAxis_copy)):
        index = xAxis.index(xAxis_copy[i])
        eachline = text_lines[index]
        lines_w.append(eachline[2]-eachline[0])

    #print(text_lines)
    #print(lines_w)
    maxw_index = lines_w.index(max(lines_w))
    #print(maxw_index)
    filter_lines.append(text_lines[xAxis.index(xAxis_copy[maxw_index])])

    if maxw_index > 0 and maxw_index < len(xAxis_copy)-1:
        for i in reversed(range(1,maxw_index+1)):
            index = xAxis.index(xAxis_copy[i])
            index_prior = xAxis.index(xAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            if ( eachline[0] - eachline_prior[2] ) < min( (eachline_prior[2]-eachline_prior[0]),(eachline[2]-eachline[0]))*xRate:
                filter_lines.insert(0,eachline_prior)
            else:
                break

        for i in range(maxw_index,len(xAxis_copy)-1):
            index = xAxis.index(xAxis_copy[i])
            index_next = xAxis.index(xAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]

            if ( eachline_next[0] - eachline[2] ) < min( (eachline_next[2]-eachline_next[0]),(eachline[2]-eachline[0]))*xRate:
                filter_lines.append(eachline_next)
            else:
                break
    elif maxw_index == 0:
        for i in range(0,len(xAxis_copy)-1):
            index = xAxis.index(xAxis_copy[i])
            index_next = xAxis.index(xAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]

            if ( eachline_next[0] - eachline[2] ) < min( (eachline_next[2]-eachline_next[0]),(eachline[2]-eachline[0]))*xRate:
                filter_lines.append(eachline_next)
            else:
                break

    elif maxw_index == (len(xAxis_copy)-1):
        for i in reversed(range(1,len(xAxis_copy))):
            index = xAxis.index(xAxis_copy[i])
            index_prior = xAxis.index(xAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            if ( eachline[0] - eachline_prior[2] ) < min( (eachline_prior[2]-eachline_prior[0]),(eachline[2]-eachline[0]))*xRate:
                filter_lines.insert(0,eachline_prior)
            else:
                break

    filter_lines = np.array(filter_lines)
    #print(filter_lines)
    return filter_lines


def textlines_merge(text_lines):
    yAxis = []
    mergeRate = 0.5 #y轴方向上的容错率阈值
    
    for line in text_lines:
        yAxis.append(line[1])

    yAxis_copy = list(yAxis)
    yAxis_copy.sort(reverse=False)

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

def color_analysis(preffixName, suffixName, textNum, textLines):

    textLinesLeft = []
    backColors = []
    for i in range(textNum+1):
        textImg = Image.open(preffixName+'_text'+ str(i)+suffixName)
        textImg = textImg.convert('RGB')
        textImg = np.asarray(textImg)

        saliencyImg = Image.open(preffixName+'_saliency'+ str(i)+suffixName)
        saliencyImg = np.asarray(saliencyImg)

        textBack_color= textImg[saliencyImg<10]
        backColors.append(np.mean(textBack_color,axis=0))

        #尝试聚类处理
        #backColor = getMainColor(textBack_color,5)
        #backColors.append(backColor)       

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

    textSizes = []
    for i in range (len(Label_index)):
        texts_label = Label_index[i]
        size = 0
        for index in texts_label:
            textline = textLines[index]
            size = size + (textline[2]-textline[0]) * (textline[3]-textline[1])
        textSizes.append(size)
    
    maxLabel = textSizes.index(max(textSizes))

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

def textRole_analysis(text_lines):
    #在红色框中区别出主副标题等
    yAxis = []

    #yRate = 1.5 #y轴方向上的容错率阈值
    #centerRate = 0.5 #x轴中心位置的容错率阈值
    
    for line in text_lines:
        yAxis.append(line[1])

    yAxis_copy = list(yAxis)
    yAxis_copy.sort(reverse=False)

    filter_lines = []
    lines_h = []
    for i in range(len(yAxis_copy)):
        index = yAxis.index(yAxis_copy[i])
        eachline = text_lines[index]
        lines_h.append(eachline[3]-eachline[1])

    maxh_index = lines_h.index(max(lines_h))
    filter_lines.append(text_lines[yAxis.index(yAxis_copy[maxh_index])])


    if maxh_index > 0 and maxh_index < len(yAxis_copy)-1:
        for i in reversed(range(1,maxh_index+1)):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            #判断二者中心点的偏移是否大于前一行宽度的X倍
            if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < 0.5*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.insert(0,eachline_prior)

        for i in range(maxh_index,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]
            #若相邻行间距大于前一行的X倍高度
            if abs((eachline_next[0] + eachline_next[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < 0.5*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.append(eachline_next)
    elif maxh_index == 0:
        for i in range(0,len(yAxis_copy)-1):
            index = yAxis.index(yAxis_copy[i])
            index_next = yAxis.index(yAxis_copy[i+1])

            eachline = text_lines[index]
            eachline_next = text_lines[index_next]
            #若相邻行间距大于前一行的X倍高度
            if abs((eachline_next[0] + eachline_next[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < 0.5*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.append(eachline_next)

    elif maxh_index == (len(yAxis_copy)-1):
        for i in reversed(range(1,len(yAxis_copy))):
            index = yAxis.index(yAxis_copy[i])
            index_prior = yAxis.index(yAxis_copy[i-1])

            eachline = text_lines[index]
            eachline_prior = text_lines[index_prior]

            if abs((eachline_prior[0] + eachline_prior[2])/2 - (text_lines[yAxis.index(yAxis_copy[maxh_index])][0] + text_lines[yAxis.index(yAxis_copy[maxh_index])][2])/2) < 0.5*(text_lines[yAxis.index(yAxis_copy[maxh_index])][2] - text_lines[yAxis.index(yAxis_copy[maxh_index])][0]):
                filter_lines.insert(0,eachline_prior)

    #filter_lines中的文字已经按照从上到下的顺序排列
    filter_lines = np.array(filter_lines)
    #print(filter_lines)
    #———————————————————如果主标题识别错误（或特别短），会出现问题，应把颜色相同，大小相似，且相邻的合并——————————

    #识别中主标题
    lines_h = []
    for i in range(len(filter_lines)):
        eachline = filter_lines[i]
        lines_h.append(eachline[3]-eachline[1])

    mianTopic_index = lines_h.index(max(lines_h))

    return filter_lines, mianTopic_index

def text_segmentation(preffixName, suffixName, textNum, textLines,f):


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
        #count, contents, location, num = text_recognition('./temp.jpg',ratio)

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
        textLines[i][0] = (x/f + boundary[0])*f
        textLines[i][1] = (y/f + boundary[1])*f
        textLines[i][2] = (x/f + boundary[2])*f
        textLines[i][3] = (y/f + boundary[3])*f

    return textLines

'''
def text_segmentation(preffixName, suffixName, textNum, textLines,f):


    for i in range(textNum+1):
        isFirst = True

        boundary = [] #边界存储顺序为左，上，右，下
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

        if num == 1:
            textImg = Image.open(imgName)
            textImg = textImg.convert('RGB')
            textImg = np.asarray(textImg)

            boundary.append(float(max(0,location[0],location[6])))
            boundary.append(float(max(0,location[1],location[3])))
            boundary.append(float(min(textImg.shape[1]-1,location[2],location[4])))
            boundary.append(float(min(textImg.shape[0]-1,location[5],location[7])))
            print boundary

            saliencyImg = Image.open(preffixName+'_saliency'+ str(i)+suffixName)
            saliencyImg = np.asarray(saliencyImg)

            textBack_color= textImg[saliencyImg<10]
            text_color = textImg[saliencyImg>220]


            backColor = np.mean(textBack_color,axis=0)
            textColor = np.mean(text_color,axis=0)
            textline = textLines[i]

            #左边
            for j in range(int(boundary[0]),textImg.shape[1]):
                averageColor = []
                for k in range(0,textImg.shape[0]):
                    if np.sqrt(np.sum(np.square(textColor - textImg[k][j]))) < 20:
                        averageColor.append(textImg[k][j]*10)
                    averageColor.append(textImg[k][j])

                averageColor = np.asarray(averageColor)
                value = np.mean(averageColor,axis=0)
                dist = np.sqrt(np.sum(np.square(backColor - value)))
                
                if dist>20 and isFirst:
                    isFirst = False
                    for m in range(int(boundary[0]),0,-1):
                        averageColor = []
                        for n in range(0,textImg.shape[0]):
                            if np.sqrt(np.sum(np.square(textColor - textImg[n][m]))) < 20:
                                averageColor.append(textImg[n][m]*10)
                            averageColor.append(textImg[n][m])

                        averageColor = np.asarray(averageColor)
                        value = np.mean(averageColor,axis=0)
                        dist = np.sqrt(np.sum(np.square(backColor - value)))
                        
                        if dist<20:
                            boundary[0] = m
                            isFirst = True
                            break
                    if not isFirst:
                        isFirst = True
                    break
                elif dist>20:
                    boundary[0] = j
                    isFirst = True
                    break
                else:
                    isFirst = False

            #上边
            for j in range(int(boundary[1]),textImg.shape[0]):
                averageColor = []
                for k in range(0,textImg.shape[1]):
                    if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                        averageColor.append(textImg[j][k]*10)
                    averageColor.append(textImg[j][k])

                averageColor = np.asarray(averageColor)
                value = np.mean(averageColor,axis=0)
                dist = np.sqrt(np.sum(np.square(backColor - value)))

                if dist>14 and isFirst:
                    isFirst = False
                    for j in range(int(boundary[1]),0,-1):
                        averageColor = []
                        for k in range(0,textImg.shape[1]):
                            if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                                averageColor.append(textImg[j][k]*10)
                            averageColor.append(textImg[j][k])

                        averageColor = np.asarray(averageColor)
                        value = np.mean(averageColor,axis=0)
                        dist = np.sqrt(np.sum(np.square(backColor - value)))

                        if dist<14:
                            boundary[1] = j
                            isFirst = True
                            break
                    if not isFirst:
                        isFirst = True
                    break
                elif dist>14:
                    boundary[1] = j
                    isFirst = True
                    break
                else:
                    isFirst = False

            #右边
            for j in range(int(boundary[2]),0,-1):

                averageColor = []
                for k in range(0,textImg.shape[0]):
                    if np.sqrt(np.sum(np.square(textColor - textImg[k][j]))) < 20:
                        averageColor.append(textImg[k][j]*10)
                    averageColor.append(textImg[k][j])


                averageColor = np.asarray(averageColor)
                value = np.mean(averageColor,axis=0)
                dist = np.sqrt(np.sum(np.square(backColor - value)))

                if dist>20 and isFirst:
                    isFirst = False
                    for j in range(int(boundary[2]),textImg.shape[1]):

                        averageColor = []
                        for k in range(0,textImg.shape[0]):
                            if np.sqrt(np.sum(np.square(textColor - textImg[k][j]))) < 20:
                                averageColor.append(textImg[k][j]*10)
                            averageColor.append(textImg[k][j])

                        averageColor = np.asarray(averageColor)
                        value = np.mean(averageColor,axis=0)
                        dist = np.sqrt(np.sum(np.square(backColor - value)))
                        
                        if dist<20:
                            boundary[2] = j
                            isFirst = True
                            break

                    if not isFirst:
                        isFirst = True
                    break
                elif dist>20:
                    boundary[2] = j
                    isFirst = True
                    break
                else:
                    isFirst = False
            #下边
            for j in range(int(boundary[3]),0,-1):

                averageColor = []
                for k in range(0,textImg.shape[1]):
                    if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                        averageColor.append(textImg[j][k]*10)
                    averageColor.append(textImg[j][k])

                averageColor = np.asarray(averageColor)
                value = np.mean(averageColor,axis=0)
                dist = np.sqrt(np.sum(np.square(backColor - value)))

                if dist>14 and isFirst:
                    isFirst = False
                    for j in range(int(boundary[3]),textImg.shape[0]):
                        averageColor = []
                        for k in range(0,textImg.shape[1]):
                            if np.sqrt(np.sum(np.square(textColor - textImg[j][k]))) < 20:
                                averageColor.append(textImg[j][k]*10)
                            averageColor.append(textImg[j][k])

                        averageColor = np.asarray(averageColor)
                        value = np.mean(averageColor,axis=0)
                        dist = np.sqrt(np.sum(np.square(backColor - value)))

                        if dist<14:
                            boundary[3] = j
                            isFirst = True
                            break
                    if not isFirst:
                        isFirst = True
                    break
                elif dist>14:
                    boundary[3] = j
                    isFirst = True
                    break
                else:
                    isFirst = False

            print textLines[i]/f
            print boundary
            x = textLines[i][0]
            y = textLines[i][1]
            textLines[i][0] = (x/f + boundary[0])*f
            textLines[i][1] = (y/f + boundary[1])*f
            textLines[i][2] = (x/f + boundary[2])*f
            textLines[i][3] = (y/f + boundary[3])*f

            #问题：中文字体因为部首原因会断开，笔画细的字不会识别出来
            print textLines[i]
            print textLines[i]/f
    return textLines
'''

   
def text_recognition(imgName,ratio):

    client = apiclient.OpenApiClient(appId,appKey,secretKey);

    fileParams = {"image":open(imgName, "rb")}
    params= {"appId":appId,"userId":"hello","groupName":"testxxx"}
    result = client.executePost("image/v1/wordrecognize",params,fileParams)
    aa = json.dumps(result,ensure_ascii=False)
    a = json.loads(aa)
    b = a['data']
    print b
    number = len(b)

    if number > 0:
        b = b[0]
        aa = json.dumps(b,ensure_ascii=False)
        a = json.loads(aa)
        count = a['count']
        contents = a['contents']
        location =  a['pt']
        location = np.array(location)
        return count, contents, location/ratio, number
    else:
        return 0,0,0,number




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

def getMainColor(im,num): 
    # im is image, num is the number of cluster
    random_state = 170
    km = KMeans(n_clusters = num , random_state = random_state)
    km.fit(im)
    labels = km.labels_
    cluster_centers = km.cluster_centers_

    area = [(labels == item).sum() for item in range(num)]
    area = np.asarray(area)

    l = km.predict(cluster_centers)
    index = np.argwhere(l == np.argmax(area))
    #return the largest aera color
    return cluster_centers[int(index)]


