import gspread # Google SpreadSheet를 사용하기 위한 라이브러리

# json 파일이 위치한 경로를 값으로 줘야 합니다.
key_path = "JSON Key PATH"
gc = gspread.service_account(key_path)
spreadsheet_url = "사용하려는 시트 url"
doc = gc.open_by_url(spreadsheet_url)

worksheet = doc.worksheet("시트1")

sum = 0
for i in range(1, 11):
        pos = "A"+str(i)
        print(pos)
        worksheet.update_acell(pos, i)
        sum += i
worksheet.update_acell('A11',"SUM = "+str(sum))
