import datetime

# 対象に応じて変更する(URLの変更がない限り変更不要)
urlLogin = "https://t.livepocket.jp/login?acroot=header-new_p_u_nl"

# チケット受付開始時間
startTime = datetime.datetime(2021, 2, 25, 22, 00, 00)  # 年, 月, 日, 時, 分, 秒
# ログイン開始時間
loginTime = datetime.datetime(2021, 2, 25, 21, 50, 30)  # 年, 月, 日, 時, 分, 秒

# 対象チケットのURL
urlTicket = "https://t.livepocket.jp/xxxxx"
# 対象チケットのid属性
ticketId = "ticket-000000"

# 枚数選択
ticketNum = "1"
