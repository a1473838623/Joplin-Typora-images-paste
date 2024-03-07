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
