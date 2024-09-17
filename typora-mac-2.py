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
