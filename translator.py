from googletrans import Translator

# 创建一个翻译器对象
translator = Translator(service_urls=['translate.google.cn'])

# 翻译中文文本为日语
text = '今天天气真好'
result = translator.translate(text, src='zh-CN', dest='ja')

# 输出翻译结果
print(result.text)