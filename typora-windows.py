# python -m pip install requests
import requests
import sys
import json
import subprocess

# WARNING: replace xxx with your joplin web clipper token
token = "xxx"
# WARNING: replace 41184 with your joplin web clipper port
port = 41184
# WARNING: replace python_exe_path with your python path, DO NOT DELELTE "r"
python_exe_path = r'C:\Users\developer\AppData\Local\Programs\Python\Python312\python.exe'
# WARNING: replace second_script_path with your second script path, DO NOT DELELTE "r"
second_script_path = r'C:\Users\developer\Desktop\files\typora-windows-2.py'

# collect args for typora-windows-2.py
args = []
for arg in sys.argv:
    # the first arg is .py file, ignore it
    if(".py" in arg):
        continue
    # the second arg is the current edting file passed by Typora
    if(".md" in arg):
        args.append(arg)
        continue
    # other arg is the local Typora-Image path passed by Typora
    url = "http://127.0.0.1:"+port+"/resources/?token="+token
    payload = {'props': '{}'}
    files=[
      ('data',('typora.png',open(arg,'rb'),'image/png'))
    ]
    headers = {}
    # upload your images to joplin resources using joplin web clipper API
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    newFilePath = "http://127.0.0.1:"+port+"/resources/"+json.loads(response.text)["id"]+"/file?token="+token
    # print newFilePath, so Typora can replace the local-typora-image path with the joplin web clipper url.
    # We can not directly using "resources/"+json.loads(response.text)["id"]+".png" since Typora think it is a illegal URL,
    # and a warning will show up.
    print(newFilePath)

    args.append(newFilePath)
    args.append("resources/"+json.loads(response.text)["id"]+".png")

# first arg is .py file, second arg is .md file, then newFilePath and "resources/"+json.loads(response.text)["id"]+".png" appear in order
# We use subprocess because Typora will wait for result of the first script and then replace the Typora_local_path with newFilePath.
# If we don't use subprocess, our replacement will be ahead of Typora's, and covered by Typora, which makes newFilePath as the finally result link.
# This is not we want, we want "resources/"+json.loads(response.text)["id"]+".png" as the result.
subprocess.Popen([python_exe_path, second_script_path] + args, creationflags=subprocess.DETACHED_PROCESS, shell=False)

sys.exit()
