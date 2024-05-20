from cryptography.fernet import Fernet
import json
import os
import paramiko
import subprocess
import json
import re
import smtplib
from email.mime.text import MIMEText
# init
########## begin ##########

os.chdir("작업 디렉토리")
pwd = os.getcwd()

# 키를 읽어오기
with open(pwd + '/키 파일', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# 암호화된 설정 파일 읽기
with open(pwd + '/enc 파일', 'rb') as enc_file:
    cipher_text = enc_file.read()

# 복호화
data = cipher_suite.decrypt(cipher_text)

# JSON 데이터 로드
server_info = json.loads(data)

########## end ##########

# ping을 통해 서버가 살아있는지 확인
def CheckServer(ip):
    try:
        alive = subprocess.run(["ping", "-c", "1", ip], capture_output=True, text=True, check=True)
        print(alive.stdout)
        if "1 received" in alive.stdout:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def UsageCPU(username, ip , port, key_pos=""):
    if key_pos == "":
        cmd = "ps -eo user,pid,ppid,%cpu,%mem,cmd --sort=-%cpu | head -n 4"
    else :
        cmd = "ssh {0}@{1} -p {2} -i {3} \"ps -eo user,pid,ppid,%cpu,%mem,cmd --sort=-%cpu | head -n 4\"".format(username, ip, port, key_pos)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # 명령어 실행 결과를 문자열로 저장
    output = result.stdout

    # 각 줄을 리스트의 요소로 변환하고, 각 요소를 공백으로 분리
    lines = [line.split(maxsplit=5) for line in output.strip().split('\n')]
    return lines

def UsageMEM(username, ip , port, key_pos=""):
    if key_pos == "":
        cmd = "ps -eo user,pid,ppid,%cpu,%mem,cmd --sort=-%mem | head -n 4"
    else :
       cmd = "ssh {0}@{1} -p {2} -i {3} \"ps -eo user,pid,ppid,%cpu,%mem,cmd --sort=-%mem | head -n 4\"".format(username, ip, port, key_pos)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # 명령어 실행 결과를 문자열로 저장
    output = result.stdout

    # 각 줄을 리스트의 요소로 변환하고, 각 요소를 공백으로 분리
    lines = [line.split(maxsplit=5) for line in output.strip().split('\n')]
    return lines

def TotalMonitoring(username, ip , port, key_pos=""):
    if key_pos == "":
        cmd = "top -b -n 1 | head -5"
    else :
      cmd = "ssh {0}@{1} -p {2} -i {3} \"top -b -n 1 | head -4\"".format(username, ip, port, key_pos)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout # 00:00:00 up  0:00,  0 users,  load average: 0.00, 0.00, 0.00
    lines = [line.strip() for line in output.strip().split('\n')]

    userMatch = re.search(r'\d+ users?', lines[0])
    loadAvgMatch = re.search(r'load average: [\d.]+, [\d.]+, [\d.]+', lines[0])
    cpuUsageMatch = re.search(r'[\d.]+ us', lines[2])
    memUsageMatch = re.search(r'[\d.]+ total', lines[3])
    freeMemMatch = re.search(r'[\d.]+ free', lines[3])
    users = userMatch.group()
    loadAvg = loadAvgMatch.group()
    cpuUsage = cpuUsageMatch.group()
    memUsage = memUsageMatch.group()
    freeMem = freeMemMatch.group()

    print(cpuUsage, memUsage, freeMem)

    pos = loadAvg.find(":") 
    loadAvg = loadAvg[pos + 1 : -1]
    arr = [value.strip() for value in loadAvg.split(',')]

    pos = users.find("u")
    users = users[:pos].strip()

    pos = cpuUsage.find("u")
    cpuUsage = cpuUsage[:pos].strip()

    pos = memUsage.find("t")
    memUsage = memUsage[:pos].strip()

    pos = freeMem.find("f")
    freeMem = freeMem[:pos].strip()

    info_dict = {
        "totalInfo" : output,
        "la1m" : arr[0],
        "la5m" : arr[1],
        "la15m" : arr[2],
        "userCnt" : users,
        "cpuUsage" : cpuUsage,
        "memUsage" : round(((float(memUsage) - float(freeMem)) / float(memUsage)) * 100, 2)
    }

    return info_dict


def SendEmail(flag, server, proc):
    if flag :       
        mb = server_info['SENDTOADMINCPU'].format(server, proc[3], proc[0], proc[1], proc[2], proc[4], proc[5])
    else :
        mb = server_info['SENDTOADMINCPU'].format(server, proc[4], proc[0], proc[1], proc[2], proc[3], proc[5])
    print(mb)
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(server_info["MAIL"], server_info["PWD"])

    msg = MIMEText(mb)
    msg['Subject'] = '[⚠️] 비이상적인 프로세스 발견 조치 바람!'
    msg['From'] = '서버 관리자'
    msg['To'] = server_info["MAIL"]
    smtp.sendmail(server_info["MAIL"], server_info["MAIL"], msg.as_string())
    
    smtp.quit()


def ForceQuitUser(username, admin="", ip="", port="", key_pos=""):
    if key_pos == "":
        cmd = "sudo pkill -9 -u " + username
    else :
        cmd = "ssh {0}@{1} -p {2} -i {3} \"sudo pkill -9 -u {4}\"".format(admin, ip, port, key_pos, username)
    
    print(cmd)
    subprocess.run(cmd, shell=True)

def ForceQuitPID(pid, admin="", ip="", port="", key_pos=""):
    if key_pos == "":
        cmd = "sudo kill -9 " + pid
    else :
        cmd = "ssh {0}@{1} -p {2} -i {3} \"sudo kill -9 {4}\"".format(admin, ip, port, key_pos, pid)
    
    print(cmd)
    subprocess.run(cmd, shell=True)