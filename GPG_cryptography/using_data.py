from cryptography.fernet import Fernet
import json

# 키를 읽어오기
with open('SOLVE.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# 암호화된 설정 파일 읽기
with open('SI.enc', 'rb') as enc_file:
    cipher_text = enc_file.read()

# 복호화
data = cipher_suite.decrypt(cipher_text)

# JSON 데이터 로드
server_info = json.loads(data)

host = server_info['NODE_HOST']
port = server_info['NODE_SSH']

print("서버 IP : ", host)
print("SSH 포트번호 : ", port)
