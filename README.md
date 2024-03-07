# Joplin-Typora-images-paste

## This is a solution for pasting image directly in Typora and upload to Joplin
If your aim is to upload images to other server(not joplin), then my solution is not your choice.

## Basic Knowledge
- If you paste your image directly to Typora, the file path is like "C:\path\to\typora\local\image\path"
- In joplin, you can see the images, but if you change your computer or upload to other place, the image link will not work.
- This is beacause Joplin use the file path like ":/resources_id"
- And if you use Typora open Joplin file(right click the note, and choose open in other editor), the joplin path will be automaticlly showed as "resouces/resources_id.png" (the real content ":/resources_id" is not changed, it just shows different).
- Joplin web clipper is a joplin build-in tool that can access local joplin resources by using API, see "https://joplinapp.org/help/api/references/rest_api/"; The common use is reading content from a web page and automaticlly copy the content to your joplin, but we can alse use it to access our data by http requests.
- You can request your images in joplin by using joplin-web-clipper-link, which is like "http://127.0.0.1:41184/resources/resources_id/file?token=your_joplin_web_clipper_token", but the link is joplin-application-based, which means if your web clipper is closed, the link unwork. So we need use joplin resources link like ":/resources_id" in Joplin or "resouces/resources_id.png" in Typora.

## Solution
- Use joplin web clipper to upload images to Joplin as resources.
- Use Typora upload-image-custom-command(see "https://support.typora.io/Upload-Image/") to run custom-command(could be a python script) and pass the typora-image-local-path and the current-markdown-file-path.

## Problem
- Typora upload-images-custom-command works when links print as lines in shell. It pass N number of images path to the command args and receive last N number of output as the link to replace.
- But Typora will think "resouces/resources_id.png" as a illegal URL and it will warn you by showing the path. Of course we can handly copy the path and replace it, we can also replace the content using Python script by writing the markdown file directly(Typora command support pass ${filepath} to the shell, which is the current markdown file path).
- The only problem makes this solution unperfect is that writing file behavior may cause a conflict between Typora and Python, I tried use file_lock, but failed.
- So although I try to fix the confict in writing file, and add retry function to retry the replacement for at most 10 times, it may aslo cause replacement fail.
- Here is the notice: Please watch the URL replacement utill your next input. And you can also copy the resource_id from the joplin_web_clipper_url and change the image link to the format "resouces/resources_id.png"

## Setps
Here is the step.
1. Click "edit outside" in joplin. Make sure that you have set typora as default markdown editor.
2. Paste your image direct to Typora.
3. Open your Typora Preference > Image > Upload service setting > custom command 
     write:  "C:\Users\developer\AppData\Local\Programs\Python\Python312\python.exe C:\Users\developer\Desktop\files\typora-windows.py  ${filepath} "
  - the "C:\Users\developer\AppData\Local\Programs\Python\Python312\python.exe" is where you install Python.
  - the C:\Users\developer\Desktop\files\typora-windows.py is the python script I will introduce below.
4. Open your joplin web clipper in joplin setting > web clipper > open web clipper service and generate your token. Please take an eye on your web clipper port (default is 41184, if not, you should replace it in your python script).
5. Create a new python script in "C:\Users\developer\Desktop\files\typora-windows.py" as below (please replace xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx with your joplin web clipper token, before using, make sure you have installed the module "requests", if not, use command "python -m pip install requests"):
```Python
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
```

6. Create a new python script in "C:\Users\developer\Desktop\files\typora-windows-2.py" as below( if your path is not replace with joplin real path, please set the sleep time from 5 to more. Retry function because you may input content during the time.sleep, it may cause replace fail, so we retry replacement for 10 times, unless you continually input in 50 seconds(which is not often) or quit editing the file before the replacement, your link will replaced by joplin link correctly. But I would recommend you to "see" the replacement happening before you input your content or quit editing):
```Python
import sys
import time

# We need to wait Typora's replacement happens first
delay_time = 5
# If we are typing during the Python's writing file, it will not cause any error but the replacement is fail 
# So we retry the function to fix it
retry_times = 10
time.sleep(delay_time)

for i in range(retry_times):
    try:
        with open(sys.argv[1], 'r+', encoding='utf-8') as file:
            file_content = file.read()
            file_content_copy = file_content
            for index, arg in enumerate(sys.argv):
                if ((".png" in arg) or (".md" in arg) or (".py" in arg)):
                    continue
                # replace newFilePath with "resources/{id}.png"
                file_content = file_content.replace(sys.argv[index], sys.argv[index + 1])
            # usually we upload at least one image, sys.argv[3] is the first image path in form of "resources/{id}.png"
            # if the first image link is replaced, then the replacement is success
            # but there is one expect: typora will question you to reload your file
            # if you click yes, it may write your old content in Typora editor directly to the file
            # which makes the replacement fail. So we retry the function at least for 3 times to make sure the replacement happened.
            if(file_content == file_content_copy and (sys.argv[3] in file_content_copy) and i > 3):
                sys.exit()
            file.seek(0)
            file.write(file_content)
            file.truncate()
        time.sleep(delay_time)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(delay_time)
sys.exit()
```
7. Upload your image by click right on the link in typora(DO NOT forget to click upload, this is important). Firstly, the link will be set to web clipper link, and after a sleep time (5 seconds) set in python script, your link will be change to joplin link(if not set, please wait more 5 seconds or you can copy the resouces_id from the web_clipper_link, and replace the old URL to the format "resources/{resources_id}.png").
8. Please note that this solution is only tested in latest version of Joplin-desktop for windows 10. Other system may need change the python script.
