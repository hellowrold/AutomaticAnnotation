# 项目简述
广告图片自动分割。输入一张广告图，自动生成结构化数据集，详细信息见[our website](http://47.98.47.1/LabelMeAnnotationTool/external.html)

# 环境
- Python2.7
- cython
- Caffe

环境配置参考：[FCIS](https://github.com/msracver/FCIS)和[CTPN](https://github.com/tianzhi0549/CTPN)

#模型下载：
产品识别模型(大约233M)下载：[OneDrive](https://1drv.ms/u/s!Am-5JzdW2XHzhqMJZmVOEDgfde8_tg)或者[BaiduYun](https://pan.baidu.com/s/1geOHioV)（密码为tmd4），把模型放入文件夹 `model`中并重命名为`fcis_coco-0000.params`

字体识别模型 (大约78M) 下载：[Google Drive](https://drive.google.com/open?id=0B7c5Ix-XO7hqQWtKQ0lxTko4ZGs) 或者 [our website](http://textdet.com/downloads/ctpn_trained_model.caffemodel), 把模型放入文件夹 `models`中并重命名为` ctpn_trained_model.caffemodel`

# 运行方式
`python style_iden.py -i test.jpg -m svm_model.dat`

其中，`-i`需要指明目标图片，`-m`需要指明所训练好的模型，具体模型训练方法参考论文《电商广告图片风格识别方法及其在广告自动化设计中的应用研究》


Enjoy It!
