from cryptography.fernet import Fernet
import json
import os
import paramiko
import subprocess
import json

# init
########## begin ##########

os.chdir("/home/master/.forRsync/")
pwd = os.getcwd()

# 키를 읽어오기
with open(pwd + '/SOLVE.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# 암호화된 설정 파일 읽기
with open(pwd + '/SI.enc', 'rb') as enc_file:
    cipher_text = enc_file.read()

# 복호화
data = cipher_suite.decrypt(cipher_text)

# JSON 데이터 로드
server_info = json.loads(data)

########## end ##########

# var.json 파일 읽기 위함
def ReadJson():
    with open(pwd+'/var.json', 'r') as f:
        jsonData = json.load(f)
        return jsonData
    
# var.json 파일 쓰기 위함
def WriteJson(jsonData):
    with open(pwd+'/var.json', 'w') as make_file:
        json.dump(jsonData, make_file, indent="\t")


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

# SSH 접속해서 동기화 명령어 실행
def SSHConnect(srcIp, srcPort, srcKeyPos, destIP, destPort):
    key = paramiko.RSAKey.from_private_key_file(server_info['MASTER_KEY'])
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(srcIp, port=srcPort, username=server_info['USER'], pkey=key)
    cmd = "sudo rsync -avruz --delete --stats -e \"ssh -p {0} -i {1}\" /home2 {2}@{3}:/".format(destPort, srcKeyPos, "root", destIP)
    print(cmd)
    try:
        stdin, stdout, stderr = s.exec_command(cmd)
        print(stdout)
        print(stderr)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
    except Exception as e:
        print(e)
    s.close()


if __name__ == "__main__":
    cloudToOp = ReadJson()

    if CheckServer(server_info['OP_HOST']) :
        if cloudToOp['Cloud_Rsync'] : 
            print("클라우드 -> 온프레미스 동기화 진행")
            SSHConnect(server_info['CLOUD_HOST'], server_info['CLOUD_SSH'], server_info['CLOUD_KEY'], server_info['OP_HOST'], server_info['OP_SSH'])
            cloudToOp['Cloud_Rsync'] = 0
            WriteJson(cloudToOp)

        else : 
            print("온프레미스 -> 클라우드 동기화")
            SSHConnect(server_info['OP_HOST'], server_info['OP_SSH'], server_info['OP_KEY'], server_info['CLOUD_HOST'], server_info['CLOUD_SSH'])

    else :
        print("동기화 대기")
        cloudToOp['Cloud_Rsync'] = 1
        WriteJson(cloudToOp)
