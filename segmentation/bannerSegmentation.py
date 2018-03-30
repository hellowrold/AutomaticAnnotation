#!/usr/bin/env python
# -*- coding: utf-8 -*-

from productPredict import productPredict
from textPredict import textPredict 
import postProcessing
import os
import scipy.misc
import Image,ImageDraw

import matlab.engine


if __name__ == '__main__':

    DEMO_IMAGE_DIR="/home/learnCode/BannerSeg/demo1/"
    imnames=os.listdir(DEMO_IMAGE_DIR)
    eng = matlab.engine.start_matlab()

    for name in imnames:

        print 111
        index = name.index('.')
        input_path=DEMO_IMAGE_DIR+name
        output_path = '../results/'+name[0:index] +'_result'+ name[index:]

        text_output_path = '../results/'+name[0:index] +'_result'+ name[index:]
        
        
        #产品处理
        predictImage,className,cutImages,masks = productPredict(input_path)
        scipy.misc.imsave('product.jpg', predictImage)
        
        '''
        #文字处理
        text_lines,f = textPredict(input_path)

        #print(text_lines)
        text_lines = postProcessing.textlines_yfilter(text_lines)
        text_lines = postProcessing.textlines_xfilter(text_lines)
        text_lines = postProcessing.textlines_merge(text_lines)
        #print(text_lines)
        '''

        originalImage = Image.open(input_path)
        originalImage = originalImage.convert('RGB')

        '''
        for i in range (len(text_lines)):
            line = text_lines[i]
            #if line[4] > 0.9:
            box = [int(line[0]/f), int(line[1]/f), int(line[2]/f), int(line[3]/f)]
            
            if os.path.exists('../textResults/'+name[0:index] +'_text'+ str(i) + name[index:]): 
                break;
            else:
                cropImage = originalImage.crop((box[0],box[1], box[2], box[3]))
                cropImage.save('../textResults/'+name[0:index] +'_text'+ str(i) + name[index:])
                eng.GetMC('../textResults/'+name[0:index] +'_text'+ str(i)+ name[index:],'../textResults/'+name[0:index] +'_saliency'+ str(i) + name[index:])

                #saliencyMap = psal.get_saliency_rbd('../textResults/'+name[0:index] +'_text'+ str(i)+ name[index:]).astype('uint8')
                #scipy.misc.imsave('../textResults/'+name[0:index] +'_saliency'+ str(i) + name[index:], saliencyMap)
            #draw.rectangle(box, fill=128)

        
        
        #确定每个字的位置
        i = len(text_lines)-1
        #text_lines = postProcessing.text_segmentation('../textResults/'+name[0:index],name[index:], i,text_lines,f)
        
        #确定颜色不一样的字体
        text_difColor,text_lines = postProcessing.color_analysis('../textResults/'+name[0:index],name[index:], i,text_lines)
        #判断每个字体的角色
        #text_lines,mianTopic_index = postProcessing.textRole_analysis(text_lines)
        '''

        
        #画图保存
        background = Image.open(input_path)
        background = background.convert('RGB')
        draw = ImageDraw.Draw(background)

        
        for each in className:
            labelname = each[1]
            for classBox in each[0]:
                draw.line([(classBox[0],classBox[1]),(classBox[2],classBox[1]),(classBox[2],classBox[3]),(classBox[0],classBox[3]),(classBox[0],classBox[1])], width=3, fill=(50,150,50,100))
                draw.text([classBox[0],classBox[1]],labelname,fill=(255,255,255))
        
        '''
        for i in range (len(text_lines)):
            line = text_lines[i]
            #if line[4] > 0.9:
            box = [int(line[0]/f), int(line[1]/f), int(line[2]/f), int(line[3]/f)]
            draw.line([(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3]),(box[0],box[1])], width=2, fill=(200,100,100,100))
        #mianTopic = [int(text_lines[mianTopic_index][0]/f), int(text_lines[mianTopic_index][1]/f), int(text_lines[mianTopic_index][2]/f), int(text_lines[mianTopic_index][3]/f)]
        
        #draw.line([(mianTopic[0],mianTopic[1]),(mianTopic[2],mianTopic[1]),(mianTopic[2],mianTopic[3]),(mianTopic[0],mianTopic[3]),(mianTopic[0],mianTopic[1])], width=1, fill=(200,100,100,100))
        #draw.rectangle([mianTopic[0],mianTopic[1],mianTopic[2],mianTopic[3]], fill=(200,100,100,100))

        
        for i in range(len(text_difColor)):
            line = text_difColor[i]
            box = [int(line[0]/f), int(line[1]/f), int(line[2]/f), int(line[3]/f)]
            draw.line([(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3]),(box[0],box[1])], width=1, fill=(0,100,200,100))
            #draw.rectangle([box[0],box[1],box[2],box[3]],fill=(200,100,0,200))
        '''

        del draw
        background.save(output_path)
        
        