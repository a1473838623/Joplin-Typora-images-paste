import sys
import time

delay_time = 5
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
                file_content = file_content.replace(sys.argv[index], sys.argv[index + 1])
            if(file_content == file_content_copy and (sys.argv[3] in file_content_copy) and i > 2):
                sys.exit()
            file.seek(0)
            file.write(file_content)
            file.truncate()
        time.sleep(delay_time)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(delay_time)
sys.exit()
