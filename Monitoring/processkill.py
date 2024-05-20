import gspread
import ServerCommand

# init
########## begin ##########

# 구글 서비스 및 스프레드 시트 접근
gc = gspread.service_account(ServerCommand.server_info['GCP_KEY'])
spreadSheetURL = ServerCommand.server_info['MONITOR_SHEET_URL']
doc = gc.open_by_url(spreadSheetURL)
workSheet = doc.worksheet("시트1")
######### end ##########

def CheckProcess(node, username="", ip="", port="", key_pos=""):
    
    cpu = ServerCommand.UsageCPU(username, ip , port, key_pos)
    if float(cpu[1][3]) >= 50 :
        cautionProc = cpu[1]
        ServerCommand.SendEmail(True, node, cautionProc)
    mem = ServerCommand.UsageMEM(username, ip , port, key_pos)
    if float(mem[1][4]) >= 60 :
        cautionProc = mem[1]
        ServerCommand.SendEmail(False, node, cautionProc)

def KillProcess(sheet):
    userList = ['B19', 'H19', 'N19']
    users = sheet.batch_get(userList)
    users = [user[0][0] if user and isinstance(user[0], list) and user[0] else '' for user in users]
    print(users)
    if users[0] != "":
        ServerCommand.ForceQuitUser(users[0])
        sheet.update_acell('B19','')
    if users[1] != "":
        ServerCommand.ForceQuitUser(users[1], ServerCommand.server_info['USER'], ServerCommand.server_info['OP_HOST'], ServerCommand.server_info['OP_SSH'], ServerCommand.server_info['MASTER_KEY'])
        sheet.update_acell('H19','')
    if users[2] != "":
        ServerCommand.ForceQuitUser(users[2], ServerCommand.server_info['USER'], ServerCommand.server_info['CLOUD_HOST'], ServerCommand.server_info['CLOUD_SSH'], ServerCommand.server_info['MASTER_KEY'])
        sheet.update_acell('N19','')


    pidList = ['D19', 'J19', 'P19']
    pids = sheet.batch_get(pidList)
    pids = [pid[0][0] if pid and isinstance(pid[0], list) and pid[0] else '' for pid in pids]
    print(pids)
    if pids[0] != "":
        ServerCommand.ForceQuitPID(pids[0])
        sheet.update_acell('D19','')
    if pids[1] != "":
        ServerCommand.ForceQuitPID(pids[1], ServerCommand.server_info['USER'], ServerCommand.server_info['OP_HOST'], ServerCommand.server_info['OP_SSH'], ServerCommand.server_info['MASTER_KEY'])
        sheet.update_acell('J19','')
    if pids[2] != "":
        ServerCommand.ForceQuitPID(pids[2], ServerCommand.server_info['USER'], ServerCommand.server_info['CLOUD_HOST'], ServerCommand.server_info['CLOUD_SSH'], ServerCommand.server_info['MASTER_KEY'])
        sheet.update_acell('P19','')



if __name__ == "__main__":
    master = []
    opNode = []
    cloudNode = []

    # 서버 상태확인, master는 꺼져있다면 실행이 안되겠죠?
    opAlive = ServerCommand.CheckServer(ServerCommand.server_info['OP_HOST'])
    cloudAlive = ServerCommand.CheckServer(ServerCommand.server_info['CLOUD_HOST'])
    
    # 각 서버 데이터 가져오기
    CheckProcess("master")
    CheckProcess("opNode", ServerCommand.server_info['USER'], ServerCommand.server_info['OP_HOST'], ServerCommand.server_info['OP_SSH'], ServerCommand.server_info['MASTER_KEY'])
    CheckProcess("cloudNode", ServerCommand.server_info['USER'], ServerCommand.server_info['CLOUD_HOST'], ServerCommand.server_info['CLOUD_SSH'], ServerCommand.server_info['MASTER_KEY'])

    KillProcess(workSheet)