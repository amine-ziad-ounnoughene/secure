import cv2
import time
import datetime
import os
import numpy as np
from PIL import Image
import requests
# you should tune this threshold to find when you are in motion or no
threshold = 450000
url = "your_camera_link"
chat_id = "your_chat_id"
API_key = "your_api_key"
link = "https://api.telegram.org/bot" + API_key + "/"
def sms(sms):
    lien = link + f"sendMessage?chat_id={chat_id}&text=" + str(sms)
    requests.get(lien)
def video(video):
    lien = link + "sendVideo?chat_id={chat_id}"
    files = {"video" : open(video,"rb")}
    resp = requests.post(lien,files=files) 

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
sum = 0
i = 0
while True:
    img = Image.open(requests.get(url, stream=True).raw)
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.fastNlMeansDenoisingColored(frame,None,10,10,7,21)
    frame_size = frame.shape[:2]
    print(sum)
    if sum > threshold:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(
                f"{current_time}.mp4", fourcc, 20, (320,240))
            print("Started Recording!")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                video(f"{current_time}.mp4")
                sms(f'check the recording live in [url}')
                os.remove(f"{current_time}.mp4")
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()
    if detection:
        out.write(frame)
    if i == 1:
       img = Image.open(requests.get(url, stream=True).raw)
       next_frame = np.array(img)
       next_frame = cv2.cvtColor( next_frame, cv2.COLOR_RGB2BGR)
       fram = cv2.fastNlMeansDenoisingColored( next_frame,None,10,10,7,21)
       sum = cv2.absdiff(src1= next_frame,src2=frame).sum()
    i = 1
 
    if cv2.waitKey(1) == ord('q'):
        break

out.release()
cv2.destroyAllWindows()
