import re
import subprocess
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from chat import sharePrompt


def sendPrompt(prompt, driver):
    # # chatgpt
    # # 寻找textarea并发送文本
    # textarea = driver.find_element(by=By.TAG_NAME,value='textarea')
    # textarea.send_keys(prompt)
    #
    # #寻找到发送的按钮
    # sendButton = driver.find_element(by=By.XPATH,value='//textarea[1]/following::button[1]')
    # sendButton.click()
    # print("send finish")

    #claude
    # 寻找textarea并发送文本
    xpath = "//div[@class='ql-editor ql-blank']"
    textarea = driver.find_element(by=By.XPATH, value=xpath)
    textarea.send_keys(prompt)
    # 输入回车发送
    textarea.send_keys(Keys.RETURN)
    print("send finish")

def getAnswer(driver,speakAnswer,updateLabel,circlenum):
    # # chatgpt
    # # 等待，当点赞按钮不可见时读取文本
    # # //div[@class='flex justify-between lg:block'][last()]//div
    # # xpath = "//div[@class='flex justify-between lg:block'][last()]/div[2]"
    # xpath = "//div[@class = 'text-gray-400 flex self-end lg:self-center justify-center mt-2 gap-2 md:gap-3 lg:gap-1 lg:absolute lg:top-0 lg:translate-x-full lg:right-0 lg:mt-0 lg:pl-2 invisible']"
    # isinvisiable = EC.invisibility_of_element_located((By.XPATH,xpath))
    # # print(isvisiable)
    # like_button = WebDriverWait(driver,999).until(isinvisiable)
    # # 找到最新的对话
    # # print(like_button)
    # answer = driver.find_element(by=By.XPATH, value='(//p)[last()-1]')
    # answer = answer.text
    # if answer=='':
    #     answer = '异次元传输中...'
    # print("get finish")
    # print(answer)

    # claude
    # 等待，当出现typing的时候读取文字
    # /html/body/div[2]/div/div[1]/div[5]/div[2]/div/div[4]/div/div[1]/div/div[2]/div/div/div[1]/div/div/div[56]/div/div/div/div/div[2]/div/div/div/div/div/div
    # 找到i标签出现的时候再进行读取
    wait = WebDriverWait(driver, 999)
    # 等待“Typing…”出现后读取
    disappear_element = wait.until(EC.invisibility_of_element_located((By.XPATH, "(//span[@class='c-mrkdwn__br'])[last()]/following::i[1]")))
    if circlenum != 0:
        answer = driver.find_element(by=By.XPATH, value="(//div[@class='p-rich_text_section'])[last()]")
        answer = answer.text
        print("网页获取的文字：",answer)
        updateLabel.emit(sharePrompt, answer)
        speakAnswer.emit()
        print("一句话读完，开始文字转语音")
    xpath = "(//span[@class='c-mrkdwn__br'])[last()]/following::i[1]"
    # span_element = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='c-mrkdwn__br'])[last()]")))
    # 等待“Typing…”消失后转语音
    i_element = wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[@class='c-mrkdwn__br'])[last()]/following::i[1]")))
    # answer = driver.find_element(by=By.XPATH, value="(//div[@class='p-rich_text_section'])[last()]")
    # answer = answer.text
    # if answer == '':
    #     answer = '异次元传输中...'
    #     print("get finish")
    #     print(answer)

    # 循环实时显示最新的内容
    while True:
        answer = driver.find_element(by=By.XPATH, value="(//div[@class='p-rich_text_section'])[last()]")
        answer = answer.text
        if answer == '':
            answer = '异次元传输中...'
        # 没说完之前都循环
        pattern = r'Typing…'
        if re.search(pattern,answer):
            print("get finish")
            print(answer)
            updateLabel.emit(sharePrompt, answer)
        else:
            break
        time.sleep(0.5)
    return answer



def linkWeb():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 使用webdriver_manager获取ChromeDriver的路径
    driver = webdriver.Chrome(options=chrome_options, executable_path='D:\chrome_driver\chromedriver.exe')
    print("检测到标题:", driver.title)
    return driver

if __name__ == '__main__':
    # p = subprocess.Popen(r"C:\Users\lv\Desktop\lauch.bat", shell=True)

    driver = linkWeb()
    # sendPrompt("444")
    getAnswer(driver)
    driver.quit()

    print("Lauch Finish")

