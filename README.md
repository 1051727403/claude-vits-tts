# GitHub Claude-vits-tts项目

**简介：使用seleminum爬取claude实现人物对话（伪）以及使用人物模型进行文字转语音**

# 语音model网盘链接

链接：https://pan.baidu.com/s/1t9jTk2lhjUu9YXqZYlF4DQ?pwd=6666 
提取码：6666



# 使用方法

这里默认已加载模型。若没有加载模型可以点击网盘链接下载并将模型拖动到model文件夹下，也可以用自己的模型，但最好把模型名字改成和网盘的类似。

1、首先准备好seleminum库去连接chrome。

查看chrom的版本，在[chrom驱动的官方网站](https://sites.google.com/chromium.org/driver/)中下载安装适配的版本（版本接近即可），并将其配置到系统环境下，具体步骤可见博客（https://blog.csdn.net/qq_51413628/article/details/130394558?spm=1001.2014.3001.5501）

2、使用bat文件或添加后缀的方式用驱动打开chrome，打开claude网站。
![image-20230722210926312](https://github.com/1051727403/claude-vits-tts/assets/70049475/8bbeebf8-3632-4896-85be-67665a86b1f4)



3、打开项目中的chat.py文件并运行，出现如下弹窗，同时控制台出现打开claude网站的网站名即为成功。

![image-20230722213458356](https://github.com/1051727403/claude-vits-tts/assets/70049475/43a7b792-4dae-498f-a202-0f0f8bac0595)

4、第一次输入需要在右下角输入框中输入并发送作为启动，后续对话则可以直接在claude中打字。

5、实测文字转语音大概在3-5s时间内，挺快的。

**录音功能未完善，点了会崩。**



# 注意

该源码仅为个人学习测试使用，请在下载后24小时内删除，不得用于商业用途，否则后果自负。任何违规使用造成的法律后果与本人无关。

