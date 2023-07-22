import re
import subprocess

import librosa
from scipy.io import wavfile
import numpy as np
import chat


def text_clear(text):
    return re.sub(r"[\n\,\(\) ]", "", text)
 #使用edge-tts把文字转成音频
def tts_func(text):
    #使用edge-tts把文字转成音频    ja-JP-NanamiNeural: 日语（女声）zh-CN-XiaoxiaoNeural: 普通话（女声御姐） zh-CN-XiaoyiNeural(普通话女萝莉) en-US-JennyNeural: 美式英语（女声）
    # 若使用日语，前后会有1重引用符xxxxx1重引用符，需要用librosa库进行裁剪
    voice = "ja-JP-NanamiNeural"
    output_file = "output.wav"
    # 构造 edge-tts 命令
    command = f"edge-tts --text '{text}' --voice {voice} --write-media {output_file}"
    # 执行 edge-tts 命令
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # 检查返回码
    if p.returncode == 0:
        print(f"音频文件已保存到 {output_file}")
        return output_file
    else:
        print(f"转换文本为音频失败 {err.decode('gbk')}")
        return None

#使用edge-tts把文字转成音频
def textTransfrom(text2tts):
    #使用edge-tts把文字转成音频
    text2tts=text_clear(text2tts)
    output_file=tts_func(text2tts)
    print("音频文件导出到：",output_file)
    #调整采样率
    sr2=44100
    wav, sr = librosa.load(output_file)
    # 裁剪，去除开头和结尾的1.3s 和 2s
    start = int(sr*1.25)
    end = -int(sr*2)
    wav = wav[start:end]
    wav2 = librosa.resample(wav, orig_sr=sr, target_sr=sr2)
    save_path2= "output_44k"+".wav"
    wavfile.write(save_path2,sr2,
                (wav2 * np.iinfo(np.int16).max).astype(np.int16)
                )
    return save_path2
if __name__ == "__main__":
    textTransfrom("今、寂滅の時です!")
    print("ok!")
