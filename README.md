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

## Steps
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
token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# WARNING: replace 41184 with your joplin web clipper port
port = "41184"
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


# After Typora replace the typora-local-image-link with web-clipper-link,
# and you didn't press "ctrl + s" to save, your content is not "commit" to current file,
# which makes python can't detect web-clipper-link and replace it with joplin-resources-link. 
# So we retry the function at least for 10 times to wait your save.(if you didn't press "ctrl + s" to save in 50 seconds, the replacement will end to fail)
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
            file.seek(0)
            file.write(file_content)
            file.truncate()
        time.sleep(delay_time)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(delay_time)
sys.exit()
```
7. Open "auto save" config in Typora.
8. Upload your image by click right on the link in typora(DO NOT forget to click upload, this is important). Firstly, the link will be set to web clipper link. After upload, I recomand you to press "ctrl + s" to save current file(although we have open "auto save", if web-clipper-link doesn't save to current file, python will not able to detect the web-clipper-link and repalce it with the correct joplin-resource-link). After a sleep time (5 seconds) set in python script, your link will be change to joplin link(if not set, please press "ctrl+s" and wait more 5 seconds or you can copy the resouces_id from the web_clipper_link, and replace the old URL to the format "resources/{resources_id}.png").
9. Please note that this solution is only tested in latest version of Joplin-desktop for windows 10. Other system may need change the python script.

## Problem
- Typora upload-images-custom-command works when links print as lines in shell. It pass N number of images path to the command args and receive last N number of output as the link to replace.
- But Typora will think "resouces/resources_id.png" as a illegal URL and it will warn you by showing the path. Of course we can handly copy the path and replace it, we can also replace the content using Python script by writing the markdown file directly(Typora command support pass ${filepath} to the shell, which is the current markdown file path).
- To avoid Typora's waring, we pass the joplin-web-clipper-link firstly to Typora, this process is smooth and no problem will show. The next step is to replace the web-lipper-link with the joplin resources link using Python to write markdown file directly.
- Although I add retry function to write file for at most 10 times, it may aslo cause replacement fail. This is because the markdown file may not save automatically after the typora-local-image-link is replaced by web-clipper-link even though we have opened "auto save" setting, and that's why we should press "ctrl + s" after the web-clipper-link shows up.
- Here is the notice: After uploading the image, if you see web-clipper-link appear, please press "ctrl+s" and observe the URL replacement to joplin-resources-link before your next typing. You can also choose to copy the "resources/resources_id" from joplin_web_clipper_link and change the image link to "resouces/resources_id.png" format since joplin_web_clipper_url already contains the resources_id.
