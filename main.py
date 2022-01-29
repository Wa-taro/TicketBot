# -*- coding: utf-8 -*-

import datetime
import os
from sys import argv
import concurrent.futures
import threading
import Ticket


def main():
    output_log("start!!")
    os.chdir(os.getcwd())
    userFileList = os.listdir("users")
    output_log(userFileList)

    with concurrent.futures.ProcessPoolExecutor(max_workers=11) as excuter:
        result_list = list(excuter.map(callTicket, userFileList))


# 時間付与してログ出力
def output_log(*str):
    print(datetime.datetime.now(), *str)


# Call ticket.py
def callTicket(userFile):
    try:
        output_log("start callTicket param=" + userFile)
        Ticket.main(userFile)
    except:
        output_log("thread error")
        return "error"
    else:
        return "success"


if __name__ == '__main__':
    main()
