import requests
import sys
import json
import subprocess

args = []
for arg in sys.argv:
    if(".py" in arg):
        continue
    if(".md" in arg):
        args.append(arg)
        continue
    url = "http://127.0.0.1:41184/resources/?token=48c9b6a0a54d393a18b1d14d58f4c4432da5a1cd499118da598f47045766dd2a0b1b8923433c4fdcf84b5d6c61350591eba4eb4d9a325a35103a6cb1af59ffab"
    payload = {'props': '{}'}
    files=[
      ('data',('typora.png',open(arg,'rb'),'image/png'))
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    newFilePath = "http://127.0.0.1:41184/resources/"+json.loads(response.text)["id"]+"/file?token=48c9b6a0a54d393a18b1d14d58f4c4432da5a1cd499118da598f47045766dd2a0b1b8923433c4fdcf84b5d6c61350591eba4eb4d9a325a35103a6cb1af59ffab"
    print(newFilePath)
    args.append(newFilePath)
    args.append("resources/"+json.loads(response.text)["id"]+".png")
second_script_path = r'C:\Users\developer\Desktop\files\typora-windows-2.py'
subprocess.Popen([r'C:\Users\developer\AppData\Local\Programs\Python\Python312\python.exe', second_script_path] + args, creationflags=subprocess.DETACHED_PROCESS, shell=False)

sys.exit()


