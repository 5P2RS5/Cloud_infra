import gspread
import ServerCommand
import time


# init
########## begin ##########

# 구글 서비스 및 스프레드 시트 접근
gc = gspread.service_account(ServerCommand.server_info['GCP_KEY'])
spreadSheetURL = ServerCommand.server_info['MONITOR_SHEET_URL']
doc = gc.open_by_url(spreadSheetURL)
workSheet = doc.worksheet("시트1")
######### end ##########

def MakeData(node, username="", ip="", port="", key_pos=""):
    cpu = ServerCommand.UsageCPU(username, ip , port, key_pos)
    mem = ServerCommand.UsageMEM(username, ip , port, key_pos)
    now = ServerCommand.TotalMonitoring(username, ip , port, key_pos)
    node.extend([cpu, mem, now])

    return node
   
def RenewSheet(sheet, list, alpha):
    # totalcpu, total memory, users
    sheet.update_acell(chr(1 + ord(alpha)) + "3", list[2]['cpuUsage'])
    sheet.update_acell(chr(3 + ord(alpha)) + "3", list[2]['memUsage'])
    sheet.update_acell(chr(5 + ord(alpha)) + "3", list[2]['userCnt'])

    # LoadAverage
    sheet.update_acell(chr(1 + ord(alpha)) + "5", list[2]['la1m'])
    sheet.update_acell(chr(3 + ord(alpha)) + "5", list[2]['la5m'])
    sheet.update_acell(chr(5 + ord(alpha)) + "5", list[2]['la15m'])

    # CPU
    for i in range(1, len(list[0])):
        for j in range(0, len(list[0][0])):
            sheet.update_acell(chr(j + ord(alpha)) + str(i + 8), list[0][i][j])
    # MEM
    for i in range(1, len(list[1])):
        for j in range(0, len(list[1][0])):
            sheet.update_acell(chr(j + ord(alpha)) + str(i + 13), list[1][i][j])

    #top result
    sheet.update_acell(chr(ord(alpha)) + "18", list[2]['totalInfo'])

    # time update
    sheet.update_acell(chr(ord(alpha) + 1) + "1", time.strftime('%c')) # 전체시간 정보 한번에




if __name__ == "__main__":
    master = []
    opNode = []
    cloudNode = []

    # 서버 상태확인, master는 꺼져있다면 실행이 안되겠죠?
    opAlive = ServerCommand.CheckServer(ServerCommand.server_info['OP_HOST'])
    cloudAlive = ServerCommand.CheckServer(ServerCommand.server_info['CLOUD_HOST'])

    # 각 서버 데이터 가져오기
    MakeData(master)
    RenewSheet(workSheet, master, 'A')
    time.sleep(60)
    # 서버가 Up이라면 수행
    if opAlive:
        MakeData(opNode, ServerCommand.server_info['USER'], ServerCommand.server_info['OP_HOST'], ServerCommand.server_info['OP_SSH'], ServerCommand.server_info['MASTER_KEY'])
        RenewSheet(workSheet, opNode, 'G')
        time.sleep(60)
    if cloudAlive:
        MakeData(cloudNode, ServerCommand.server_info['USER'], ServerCommand.server_info['CLOUD_HOST'], ServerCommand.server_info['CLOUD_SSH'], ServerCommand.server_info['MASTER_KEY'])
        RenewSheet(workSheet, cloudNode, 'M')