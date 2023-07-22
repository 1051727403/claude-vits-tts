import re
import subprocess

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def linkWeb():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 使用webdriver_manager获取ChromeDriver的路径
    driver = webdriver.Chrome(options=chrome_options, executable_path='D:\chrome_driver\chromedriver.exe')
    print("检测到标题:", driver.title)
    return driver



if __name__ == '__main__':
    # # p = subprocess.Popen(r"C:\Users\lv\Desktop\lauch.bat", shell=True)
    # driver = linkWeb()
    # # //*[@id="1684234368.736979"]/div/div/div/div/div[2]/div/div/div/div/div/div
    # answer = driver.find_element(by=By.XPATH, value="(//div[@class='p-rich_text_section'])[last()]")
    # answer = answer.text
    # print(answer)
    #
    #
    # print("Lauch Finish")
    text = "えっ、まだ朝食を食べていないの?大変だわ。早く朝食を食べないと体が大変なことになるよ。私が作ったサンドイッチを食べましょうか?" \
           "\n<line>\n" \
           "啊,还没吃早餐吗?太糟糕了。不早点吃早餐的话身体会有大麻烦的。要不要吃我做的三明治? （已编辑） "
    # 正则表达式模式
    pattern = r'.*(?=\n<line>)'
    if re.search(pattern, text):
        print("匹配成功")
        match = re.search(pattern, text)
        japaneseAnswer = match.group(0)
        print(japaneseAnswer)  # 输出：私はChatGPTと言います。
    else:
        print("匹配失败")