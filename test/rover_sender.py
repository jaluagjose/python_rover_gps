import requests

url = "http://10.107.30.122:30932/marker/rover"

payload = {'lat': '38.145520',
           'lon': '-76.522913'}

files=[
    ('content_file',('lorem.txt',open('/home/jetson/robot_autonomy/rover_mission/videos/interview.json','rb'),'text/plain')),
    ('video_file',('test1.mp4',open('/home/jetson/robot_autonomy/rover_mission/videos/person_detection_output.mp4','rb'),'video/mp4'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
