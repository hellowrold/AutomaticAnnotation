# 项目简述
广告图片自动分割。输入一张广告图，自动生成结构化数据集，详细信息见[our website](http://47.98.47.1/LabelMeAnnotationTool/external.html)

# 环境
- Python2.7
- cython
- Caffe

环境配置参考：[FCIS](https://github.com/msracver/FCIS)和[CTPN](https://github.com/tianzhi0549/CTPN)

# 模型下载：
产品识别模型(大约233M)下载：[OneDrive](https://1drv.ms/u/s!Am-5JzdW2XHzhqMJZmVOEDgfde8_tg)或者[BaiduYun](https://pan.baidu.com/s/1geOHioV)(密码为tmd4)，把模型放入文件夹 `model`中并重命名为`fcis_coco-0000.params`

字体识别模型 (大约78M) 下载：[Google Drive](https://drive.google.com/open?id=0B7c5Ix-XO7hqQWtKQ0lxTko4ZGs), 把模型放入文件夹 `models`中并重命名为` ctpn_trained_model.caffemodel`

# 运行方式
`python ./segmentation/infoExtraction.py`

Enjoy It!
