from cryptography.fernet import Fernet
import os

# 비밀 키 생성
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 암호화할 데이터 JSON 형식으로 생성
server_info = b"""
{
    "USER": "root"
    "MASTER_KEY": "마스터 키 위치",
    "OP_HOST": "온프레미스 IP주소",
    "OP_SSH": 온프레미스 SSH 포트번호,
    "OP_KEY": "온프레미스 접속 키 위치",
    "CLODU_HOST": "클라우드 IP주소",
    "CLOUD_SSH": 클라우드 SSH 포트번호,
    "CLOUD_KEY": "클라우드 접속 키 위치",
}
"""

# 암호화
data = cipher_suite.encrypt(server_info)

# 작업 디렉토리 변경
os.chdir("작업 디렉토리")
# pwd 변수에 작업 디렉토리 저장
pwd = os.getcwd()

# print(pwd)

# 암호화된 데이터와 키 파일로 생성
with open(pwd + "/SI.enc", 'wb') as enc_file:
    enc_file.write(data)

with open(pwd + '/SOLVE.key', 'wb') as key_file:
    key_file.write(key)
