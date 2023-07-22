import subprocess



if __name__ == "__main__":
    p=subprocess.Popen(r"E:\BaiduNetdiskDownload\ai\So-VITS-SVC\so-vits-svc\app.py", shell=True)
    print(p)
    print(p.communicate())
    print("ok!")
