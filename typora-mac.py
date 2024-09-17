# python -m pip install requests
import requests
import sys
import json
import subprocess

# WARNING: replace xxx with your joplin web clipper token
token = "xxxxxxxxxxxxxxxxxxxxxxxx"
# WARNING: replace 41184 with your joplin web clipper port
port = "41184"
# WARNING: replace python_exe_path with your python path, DO NOT DELELTE "r"
python_exe_path = r'/Users/username/Documents/python_venv/bin/python3'
# WARNING: replace second_script_path with your second script path, DO NOT DELELTE "r"
second_script_path = r'/Users/username/Documents/self_sh/typora-mac-2.py'

# collect args for typora-mac-2.py
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

subprocess.Popen([python_exe_path, second_script_path] + args,
                 start_new_session=True,  # Detach the process
                 stdout=subprocess.DEVNULL,  # Suppress output to make sure it doesn't block
                 stderr=subprocess.DEVNULL)  

sys.exit()
