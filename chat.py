import os
import re
import subprocess
import sys
import queue
import sys
import threading
import time
import wave
import winsound
import openai
import pyaudio
import urllib3
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTextEdit
from playsound import playsound
from subprocess import Popen

import MoeGoe
import predict_speech_file
import send_text_to_web
import speech_recorder

# 打开 WAV 文件


# 使用planA调用api时打开，使用planB时需要注释，会导致崩溃，显示驱动和浏览器不兼容
# os.environ["http_proxy"] = "http://127.0.0.1:1081"
# os.environ["https_proxy"] = "https://127.0.0.1:1081"
openai.api_key = ""



# msgList = []
# # 调用GPT接口
# def chatGpt(prompt,count):
#     # 将当前信息加入到队列中，保留三轮的历史信息，并每三轮添加一次设定
#     print("count:",count)
#     # print("personilitySetting:",personilitySetting)
#     if count == 0:
#         prompt = personilitySetting+prompt
#     print("prompt:",prompt)
#     nowPrompt = {"role": "user", "content": prompt}
#     # 将当前信息加入到队列中，保留三轮的历史信息，并每三轮添加一次设定
#     if len(msgList)==6:
#         del msgList[0]
#         msgList.append(nowPrompt)
#     else:
#         msgList.append(nowPrompt)
#
#     completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=msgList,
#         temperature=0.5,
#         max_tokens=200
#     )
#     # print("comoletion:", completion)
#     chatGptResult = completion.choices[0].message.content
#     answer = {"role": "assistant", "content": chatGptResult}
#     # 将回复放入
#     if len(msgList)==6:
#         del msgList[0]
#         msgList.append(answer)
#     else:
#         msgList.append(answer)
#
#     return chatGptResult


# 使用自动化脚本连接网页获取回复，PlanB，该方案无需消耗token
def sendMsg(prompt,driver):
    send_text_to_web.sendPrompt(prompt,driver)


# 共享变量，每次update的时候更新
sharePrompt = ''
que = queue.Queue()
# 检测gpt返回的文本
def detectAnswer(updateLabel,driver,speakAnswer):
    global sharePrompt
    # 判断是否讲完话,通过当前answer和上一个answer相同，且上上个answer不是‘异次元传输中...’或是和上个answer相同判断
    global que
    que.put('异次元传输中...')
    que.put('异次元传输中...')
    que.put('异次元传输中...')

    count = 0
    circlenum = 0
    while True:
        # 找到最新的对话
        try:
            # 等待找到最新的对话,当元素为invilid时进行读取
            answer = send_text_to_web.getAnswer(driver,speakAnswer,updateLabel,circlenum)

        except Exception:
            count=count+1
            print("当前未检测到回答！",count)
            answer = '异次元传输中...'

        print("get finish")
        print(answer)

        updateLabel.emit(sharePrompt ,answer)
        # chatgpt
        # # 新的放入，旧的取出
        # que.put(answer)
        # que.get()
        #
        # # 取出全部的三个
        # old = que.get()
        # mid = que.get()
        # new = que.get()
        #
        # #判断是否一句话说完
        # if new==mid and new!='异次元传输中...' and new!='Typing…' and new != old:
        #     # 正则表达式模式
        #     pattern = r"Typing…"
        #     if re.search(pattern,new):
        #         print("还没说完话。")
        #     else:
        #         # 一句话说完了
        #         speakAnswer.emit()
        #         updateLabel.emit(sharePrompt, answer)
        #         print("一句话读完，开始文字转语音")
        #
        # # 放回
        # que.put(old)
        # que.put(mid)
        # que.put(new)
        circlenum= circlenum+1
        time.sleep(1)

# 线程和信号机制
class Worker(QThread):
    recordFinished = pyqtSignal()
    recognizeFinish = pyqtSignal(str)
    speakAnswer = pyqtSignal()
    speakResultFinish = pyqtSignal(str)
    updateLabel = pyqtSignal(str,str)
    def __init__(self,label,func_type,driver=0,prompt ="Nanami",answer='',chatResult='',count = 0):
        super().__init__()
        self.label = label
        self.func_type=func_type
        self.prompt = prompt
        self.answer = answer
        self.chatResult = chatResult
        self.count = count
        self.driver = driver
    def run(self):
        if self.func_type=='record_speech':
            # 录音
            duration = 5
            self.prompt = "开始语音识别，录音时间为"+str(duration)+"s"
            self.updateLabel.emit(self.prompt)
            speech_recorder.record_wave("output.wav", duration=duration,updateLabel=self.updateLabel,prompt=self.prompt)  # target=speech_save_as_wav.record_speech())
            self.recordFinished.emit()
        elif self.func_type=='recognize_speech':
            # 语音识别
            prompt = predict_speech_file.record_speech()
            self.recognizeFinish.emit(prompt)
        elif self.func_type=='chatGptApi':
            # 传入chatgpt
            print("将prompt传入到chatgpt中")
            # 方案一：采用3.5api，消耗token，较慢
            # chatResult = chatGpt(self.prompt,self.count)
            # 方案二：采用较低版本模型，连接官方网页，实现快速对话,用自动化发送文本
            # 更新会话
            self.updateLabel.emit(self.prompt, self.answer)
            print("已发送信息信息")
            sendMsg(self.prompt, driver=self.driver)
            # print("chatgpt中获取到返回的信息")
        elif self.func_type=='detectAnswer':
            print("开启循环检测字符串并实时显示")
            detectAnswer(updateLabel=self.updateLabel,driver=self.driver,speakAnswer = self.speakAnswer)

# 创建一个透明色的窗口
class TransparentWidget(QWidget):
    def __init__(self,driver,*args,**kwargs):
        super().__init__(*args, **kwargs)
        # 询问轮数
        self.count = 0
        self.driver = driver
        self.offset = None
        self.prompt = ''
        self.answer = ''
        self.lock = threading.Lock()
        self.setWindowTitle('Transparent Widget')
        self.setGeometry(1220, 780, 700, 250)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 左侧布局600*300-----------------------------------------------------------
        self.label = QTextEdit(self)
        #设置字体颜色#ed1566

        self.label.setStyleSheet("border: 1px solid white;background-color: transparent;")
        self.label.setTextColor(QColor("#ed1566"))
        # 设置字体大小
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.set_prompt("")
        self.label.setText(self.prompt)
        # 边框样式
        # self.label.setStyleSheet("border: 1px solid;")
        # padding = 20
        # self.label.setGeometry(QRect(padding, padding,600-padding,300-padding))
        # 设置自动换行
        # self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)

        # 添加按钮
        self.buttonRecord = QPushButton("开始录音")
        self.buttonRecord.clicked.connect(self.runButtonThread)

        #右侧布局200*300-----------------------------------------------------------
        self.textarea = QTextEdit()
        self.textarea.setLineWrapMode(self.textarea.WidgetWidth)
        self.textarea.setStyleSheet("border: 1px solid white;background-color: rgba(255, 255, 255, 100);")
        font = QFont()
        font.setPointSize(10)
        self.textarea.setFont(font)
        # 创建发送按钮
        self.buttonSendMsg = QPushButton("发送文本")
        self.buttonSendMsg.clicked.connect(self.runButtonSendMsg)

        # 设置布局
        # 总体横向布局
        layoutRow =QHBoxLayout()

        # 左侧垂直布局600*300
        layoutLeft = QVBoxLayout()
        layoutLeft.addWidget(self.buttonRecord)
        layoutLeft.addWidget(self.label)
        layoutRow.addLayout(layoutLeft,3) #左侧占据3/4


        # 右侧垂直布局200*300
        layoutRight = QVBoxLayout()
        layoutRight.addWidget(self.textarea)
        layoutRight.addWidget(self.buttonSendMsg)
        layoutRow.addLayout(layoutRight,1)#右侧占据1/4

        #将布局加入到主页面中去
        self.setLayout(layoutRow)
        # 设置鼠标追踪
        self.label.setMouseTracking(True)
        self.setMouseTracking(True)




    def set_prompt(self,prompt):
        self.prompt = prompt
        self.label.setText(self.prompt)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 边框透明色
        painter.setPen(QColor(255, 255, 255,0))

        gradient = QLinearGradient(0, 0, self.width(), self.height())  # 创建一个线性渐变画刷
        gradient.setColorAt(0, QColor(140, 248, 252, 200))
        gradient.setColorAt(1, QColor(196, 112, 236, 200))
        painter.setBrush(gradient)
        painter.drawRect(self.rect())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + (event.pos() - self.offset))
        else:
            super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = None
        else:
            super().mouseReleaseEvent(event)
    # 更新    self.prompt = prompt
    #         self.answer = answer
    #         sharePrompt = self.prompt
    def updateLabel(self,prompt,answer):
        # 修改共享变量sharePrompt
        self.lock.acquire()
        self.prompt = prompt
        self.answer = answer
        global sharePrompt
        sharePrompt = self.prompt
        showText = 'My> '+self.prompt+'\n'+'ななみ> '+self.answer
        self.lock.release()
        self.label.setPlainText(showText)
    # 跳过语音识别，转而发送textarea中的文字进行chat
    def runButtonSendMsg(self):
        prompt = self.textarea.toPlainText()
        print("文字输入prompt: ",prompt)
        self.updateLabel(prompt,'')
        # 清除输入文字
        self.textarea.clear()
        print("My> ", prompt)
        # showText = "My> " + prompt
        # self.label.setText(showText)
        # 先发送消息再检测，保证音频不会过早的生成
        self.worker = Worker(self.label, 'chatGptApi',prompt=self.prompt,count=self.count,driver=self.driver)
        self.worker.updateLabel.connect(self.updateLabel)
        self.worker.start()
        # 初始发送的时候开始检测
        if self.count==0:
            self.detect = Worker(self.label, 'detectAnswer', driver=self.driver)
            self.detect.updateLabel.connect(self.updateLabel)
            self.detect.speakAnswer.connect(self.speakAnswer)
            self.detect.start()
        self.count = self.count + 1


    # 按下按钮后启动录音线程
    def runButtonThread(self):
        # 创建线程，并设置信号槽并启动
        try:
            self.worker = Worker(self.label,func_type='record_speech',driver=self.driver)
            self.worker.recordFinished.connect(self.on_recordFinished)
            self.worker.updateLabel.connect(self.updateLabel)
            self.worker.start()
        except Exception:
            print("error:",Exception)

    #录音操作完成后的函数
    def on_recordFinished(self):
        self.prompt = "录音完成，开始识别..."
        self.updateLabel(self.prompt)
        # self.label.setText(self.prompt)
        # 创建线程，并设置信号槽并启动识别程序
        self.worker = Worker(self.label, 'recognize_speech')
        self.worker.recognizeFinish.connect(self.on_recognizeFinish)
        self.worker.updateLabel.connect(self.updateLabel)
        self.worker.start()
    #识别操作完成后的操作
    def on_recognizeFinish(self,prompt):
        print("语音识别完毕")
        # prompt = "一句话概括水的作用"
        print("My> ", prompt)
        self.prompt=prompt
        self.updateLabel(self.prompt)
        # showText = "My> " + prompt
        # self.label.setText(showText)
        #启动CHATGPT API 对话线程
        self.worker = Worker(self.label, 'chatGptApi',prompt=prompt,driver=self.driver)
        self.worker.updateLabel.connect(self.updateLabel)
        self.worker.start()
    # vits+tts文字转语音
    def speakAnswer(self):
        print("一句话读完，开始文字转语音")
        # 方案二：使用vits+tts直接从文本转语音，调用MoeGoe.py的speakout函数
        # 生成音频文件
        japaneseAnswer = "正則一致ミス、日本語ではない書き出しです"
        pattern = r'.*(?=\n<line>)'
        print("speak模块获取的answer",self.answer)
        if re.search(pattern, self.answer):
            print("正则匹配成功!")
            match = re.search(pattern, self.answer)
            japaneseAnswer = match.group(0)
            print("正则表达式获取需要speak的语言，截取<line>之前的日语",japaneseAnswer)  # 输出：私はChatGPTと言います。
        else:
            print("正则匹配出现错误")
        t1 = threading.Thread(target=MoeGoe.speakout,args=(japaneseAnswer,))
        t1.start()
        t1.join()

        print("播放语音")
        # 播放语音
        t2 = threading.Thread(target=speakOut)
        t2.start()



        # 方案一，生成语音后通过so-vits-svc变声
        # # 生成音频文件
        # t1 = threading.Thread(target=textTransfrom,args=(self.answer,))
        # t1.start()
        # t1.join()
        #
        # print("播放语音")
        # # 播放语音
        # t2 = threading.Thread(target=speakOut)
        # t2.start()


# def text_clear(text):
#     return re.sub(r"[\n\,\(\) ]", "", text)
#  #使用edge-tts把文字转成音频
# def tts_func(text):
#     #使用edge-tts把文字转成音频    ja-JP-NanamiNeural: 日语（女声）zh-CN-XiaoxiaoNeural: 普通话（女声御姐） zh-CN-XiaoyiNeural(普通话女萝莉) en-US-JennyNeural: 美式英语（女声）
#     # 若使用日语，前后会有1重引用符xxxxx1重引用符，需要用librosa库进行裁剪
#     voice = "zh-CN-XiaoyiNeural"
#     output_file = "output.wav"
#     # 构造 edge-tts 命令
#     command = f"edge-tts --text '{text}' --voice {voice} --write-media {output_file}"
#     # 执行 edge-tts 命令
#     p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     out, err = p.communicate()
#     # 检查返回码
#     if p.returncode == 0:
#         print(f"音频文件已保存到 {output_file}")
#         return output_file
#     else:
#         print(f"转换文本为音频失败 {err.decode('gbk')}")
#         return None
#
# #使用edge-tts把文字转成音频
# def textTransfrom(text2tts):
#     #使用edge-tts把文字转成音频
#     text2tts=text_clear(text2tts)
#     output_file=tts_func(text2tts)
#     print("音频文件导出到：",output_file)
#     #调整采样率
#     sr2=44100
#     wav, sr = librosa.load(output_file)
#     wav2 = librosa.resample(wav, orig_sr=sr, target_sr=sr2)
#     save_path2= "output_44k"+".wav"
#     wavfile.write(save_path2,sr2,
#                 (wav2 * np.iinfo(np.int16).max).astype(np.int16)
#                 )
#     return save_path2


def speakOut(output_file=r"D:\DEEP LEARNING\CHATGPT\result_audio\output.wav"):
    print("paly audio")
    playsound(output_file)


def init(driver):
    app = QApplication(sys.argv)
    widget = TransparentWidget(driver=driver)
    widget.show()
    return app,widget



if __name__ == '__main__':
    prompt = "Nanami"
    # 连接web
    driver = send_text_to_web.linkWeb()
    # send_text_to_web.getAnswer(driver)
    app,widget=init(driver=driver)
    widget.set_prompt(prompt)
    sys.exit(app.exec_())
    # 初始化

# 一句话概括水的作用
# 水是生命之源，我们需要保护它
