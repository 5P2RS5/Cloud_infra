from cryptography.fernet import Fernet

# 비밀 키 생성
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 암호화할 데이터 JSON 형식으로 생성
server_info = b"""
{
    "NODE_HOST": "XXX.XXX.XXX.XXX",
    "NODE_SSH": "22"
}
"""

# 암호화
data = cipher_suite.encrypt(server_info)

# 암호화된 데이터와 키를 파일에 저장
with open('SI.enc', 'wb') as enc_file:
    enc_file.write(data)

with open('SOLVE.key', 'wb') as key_file:
    key_file.write(key)