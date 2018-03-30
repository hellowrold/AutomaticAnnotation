# 项目简述
本项目的主要目的是通过给定一张图片，判断其所属的风格类别。可能的风格类别有13种，分别是浪漫(Romantic)、甜美(Pretty)、整洁(Clear)、自然(Natural)、随意(Casual)、优雅(Elegant)、休闲(Cool Casual)、时髦(Chic)、奢侈(Gorgeous)、动感(Dynamic)、古典(Classic)、华丽(Dandy)、现代(Modern)。

# 环境
- numpy
- matlab 2016R
- pymatlab

# 运行方式
`python style_iden.py -i test.jpg -m svm_model.dat`

其中，`-i`需要指明目标图片，`-m`需要指明所训练好的模型，具体模型训练方法参考论文《电商广告图片风格识别方法及其在广告自动化设计中的应用研究》


Enjoy It!
