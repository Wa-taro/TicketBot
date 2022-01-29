# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import threading


import Parameters
import TicketParam
import env

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import configparser

# メモ 購入ボタンのタグ
# "<section id=\"submit\" class=\"center-btn fixed-btn\"> <p class=\"button register center-block btn-procedure\" style=\"display: block;\"><button class=\"register_input_submit register_input_submit_pink\" data-role=\"none\" type=\"submit\" onclick=\"return buy_ticket();\">お申込み / 購入手続き</button></p> <p class=\"button register center-block btn-proceed\" style=\"display: none;\"><button class=\"register_input_submit register_input_submit_pink register_input_submit_blue\" data-role=\"none\" type=\"submit\" onclick=\"return buy_ticket();\">チケット申込み / 購入へ進む</button></p> <p class=\"button register center-block btn-procedure-pc-only\"><button class=\"register_input_submit register_input_submit_pink\" data-role=\"none\" type=\"submit\" onclick=\"return buy_ticket();\">お申込み / 購入手続き</button></p> </section>"


# main
def main(userFile):

    param = set_parameters(userFile)

    # Chromeの設定変更
    options = webdriver.ChromeOptions()
    # headlessモードを使用する
    if env.headlessModeFlg:
        options.add_argument('--headless --disable-gpu')
    # デスクトップ通知無効
    options.add_argument('--disable-desktop-notifications')
    # extension(拡張)無効
    options.add_argument("--disable-extensions")
    # シークレットモード
    options.add_argument('--incognito')
    # 言語設定
    options.add_argument('--lang=ja')
    # 画像を読み込まないで軽くする
    options.add_argument('--blink-settings=imagesEnabled=false')

    options.page_load_strategy = 'none'

    # chromeドライバーのPathを指定しウィンドウを開く(環境に合わせて変更する)
    driver = webdriver.Chrome(options=options,
                              executable_path=env.chromeDriverPath)

    # ウィンドウサイズを指定
    driver.set_window_size(1280, 720)

    # Call functions
    doLoginFlg = False
    for i in range(10):
        try:
            do_login(driver, param)
        except Exception as e:
            import traceback
            traceback.print_exc()
            output_log(param.userFile, "error do_login(). refresh and retry")
            # cookies,chashをクリアして更新
            driver.delete_all_cookies()
            driver.refresh()
        else:
            doLoginFlg = True
            break
    if not doLoginFlg:
        print(param.userFile, "do_login() Failure")
        return

    buyTicketFlg = False
    for i in range(10):
        try:
            buy_ticket(driver, param)
        except Exception as e:
            import traceback
            traceback.print_exc()
            output_log(param.userFile, "error buy_ticket(). refresh and retry")
            driver.refresh()
        else:
            buyTicketFlg = True
            break
    if not buyTicketFlg:
        print(param.userFile, "buy_ticket() Failure")
        return

    for i in range(10):
        try:
            do_settlement(driver, param)
        except Exception as e:
            import traceback
            traceback.print_exc()
            output_log(param.userFile,
                       "error do_settlement. refresh and retry")
            driver.refresh()
        else:
            output_log(param.userFile, "completed!!")
            break
    # sleepTime秒間画面を起動しておく
    sleepTime = 10
    output_log(param.userFile, "sleep:" + str(sleepTime))
    time.sleep(sleepTime)


# ファイルからパラメータを取得してセットする。そして返す
def set_parameters(userFile):
    output_log(userFile, "start set_parameters")
    # 初期化
    param = Parameters.Parameters()

    # TicketPara.pyから取得
    param.userFile = userFile

    param.urlLogin = TicketParam.urlLogin
    param.loginTime = TicketParam.loginTime
    param.urlTicket = TicketParam.urlTicket
    param.ticketId = TicketParam.ticketId
    param.ticketNum = TicketParam.ticketNum
    param.startTime = TicketParam.startTime

    # Userごとの設定
    userConfig = configparser.ConfigParser()
    # 作業ディレクトリをpyファイルがあるディレクトリに移動
    output_log(param.userFile, "prama1 " + userFile)
    # configファイルをread
    userConfig.read('users/' + userFile, 'utf-8')

    # paramDtoへの代入
    param.loginUser = userConfig.get('USER', 'loginUser')
    param.loginPassword = userConfig.get('USER', 'loginPassword')
    param.delay = userConfig.get('USER', 'delay')

    output_log(param.userFile,
               "------------------parameters start------------------")
    output_log(param.userFile, "urlLogin=" + param.urlLogin)
    output_log(param.userFile, "loginTime=" +
               param.loginTime.strftime('%Y-%m-%d %H:%M:%S'))
    output_log(param.userFile, "loginUser=" + param.loginUser)
    output_log(param.userFile, "loginPassword=" + param.loginPassword)
    output_log(param.userFile, "urlTicket=" + param.urlTicket)
    output_log(param.userFile, "ticketId=" + param.ticketId)
    output_log(param.userFile, "ticketNum=" + param.ticketNum)
    output_log(param.userFile, "startTime=" +
               param.startTime.strftime('%Y-%m-%d %H:%M:%S'))
    output_log(param.userFile, "delay=" + str(param.delay))
    output_log(param.userFile,
               "--------------------parameters end--------------------")
    output_log(param.userFile, "end set_parameters")

    return param


# ログイン処理
def do_login(driver, param):
    output_log(param.userFile, "start do_login")
    sleep_until_time(param.loginTime, param.delay, param.userFile)
    # ログイン画面を開く
    driver.get(param.urlLogin)
    # ユーザー,パスワードを入力
    driver.find_element_by_css_selector(
        "input#email").send_keys(param.loginUser)
    driver.find_element_by_css_selector(
        "input#password").send_keys(param.loginPassword)
    # ログインボタンをクリック
    driver.find_element_by_css_selector("button[name=action]").click()
    output_log(param.userFile, "end do_login")

    time.sleep(1)
    # チケットの画面を開く
    driver.get(param.urlTicket)


# チケット購入処理
def buy_ticket(driver, param):
    output_log(param.userFile, "start buy_ticket")

    # 画面infomationをlogに出力
    infoText = driver.find_element_by_xpath(
        "//section[@id='navigation']/div/p").text
    if infoText:
        output_log(param.userFile, "   Infomation=["+infoText+"]")
    else:
        output_log(param.userFile, "no infomation")

    try:
        accessLimitText = driver.find_element_by_xpath(
            "//section[@id='access_limit']/section/p[2]").text
        output_log(param.userFile,
                   "   Access limit=["+accessLimitText+"]")
    except:
        output_log(param.userFile, "no access limit")

    # html書き換え
    buy_ticket_overwrite_html(driver, param)

    # ドロップダウンからチケットの枚数を選択
    dropDown = driver.find_element_by_css_selector(
        "select#" + param.ticketId)
    Select(dropDown).select_by_value(param.ticketNum)

    # 時間が来るまで待機
    sleep_until_time(param.startTime, param.delay, param.userFile)

    # 購入ボタンをクリック
    driver.find_element_by_xpath("//section[@id='submit']/p[3]/button").click()

    cur_url = driver.current_url
    if not "confirm" in cur_url:
        output_log(param.userFile, "url is Illegal")
        raise Exception
    output_log(param.userFile, "end buy_ticket")


# 決済処理
def do_settlement(driver, param):
    output_log(param.userFile, "start do_settlement")
    # 支払い方法の選択
    driver.find_element_by_css_selector(
        "p#other_payment_method_select_img").click()
    # ドロップダウンからコンビニの種類を選択
    dropDown = driver.find_element_by_css_selector(
        "select#cvs_select")
    Select(dropDown).select_by_value("002")

    # 「上記内容に同意しました」にチェック
    driver.find_element_by_css_selector("input#agreement_check_lp").click()

    # 確定処理
    if not env.debugModeFlg:
        output_log(param.userFile, "click submit-btn")
        driver.find_element_by_xpath("//li[@id='submit-btn']/button").click()

    output_log(param.userFile, "end do_settlement")


# 指定の時間までsleep
def sleep_until_time(targettime, delay, userFile):
    # 現在日時(エポック秒)を取得
    now = time.time()
    # 時間を過ぎていた場合1秒間sleep
    if (now < targettime.timestamp()):
        # 待機時間を出力
        output_log(userFile, "sleep until " +
                   targettime.strftime('%Y-%m-%d %H:%M:%S'))
        output_log(userFile, "sleep:", targettime.timestamp(), " - ",
                   now, "+", delay, " = ",
                   targettime.timestamp() - now + float(delay))
        # 時間が来るまで待機(ディレイをかける)
        time.sleep(targettime.timestamp() - now + float(delay))
    else:
        output_log(userFile, "sleep:1 seccond")
        time.sleep(1)


# 都合の良いようにhtmlを書き換える
def buy_ticket_overwrite_html(driver, param):
    output_log(param.userFile, "start buy_ticket_overwrite_html")
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # 対象チケットのdisable属性を削除する
        driver.execute_script(
            "document.getElementById('" + param.ticketId + "').removeAttribute('disabled')")
    except:
        # 対象チケットを生成する

        # purchase_formフォームが存在する場合それに、存在しない場合contentsに作成する
        try:
            output_log(param.userFile, "Generate TicketID in purchase_form")
            driver.execute_script(
                "var ticket_selection=purchase_form.appendChild(document.createElement('select'));"
                "ticket_selection.id='"+param.ticketId+"';")
        except:
            print(param.userFile, "Failure")
            output_log(param.userFile, "Generate TicketID in contents")
            driver.execute_script(
                "var ticket_selection=contents.appendChild(document.createElement('select'));"
                "ticket_selection.id='"+param.ticketId+"';")
        driver.execute_script(
            "document.getElementById('"+param.ticketId+"').setAttribute('data-role','none');")
        driver.execute_script(
            "document.getElementById('"+param.ticketId+"').setAttribute('class','event_ticket_count ticket_type_normal surcharge_ticket group_id_134031 ticket_select');")
        driver.execute_script(
            "document.getElementById('"+param.ticketId+"').setAttribute('onchange',\"check_same_ticket(362088, 134031, 'normal');check_order_limited_ticket(362088, 134031);\");")
        # option 1生成
        driver.execute_script(
            "var option1 = document.createElement('option');"
            "option1.id='option1';"
            "option1.value='1';"
            "option1.text='1枚';"
            "document.getElementById('" + param.ticketId + "').appendChild(option1);")

    # 購入ボタンが無ければ生成する
    buyAreaList = soup.find_all(id="submit")
    if len(buyAreaList) == 0:

        # purchase_formフォームが存在する場合それに、存在しない場合contentsに作成する
        try:
            output_log(param.userFile,
                       "Generate subumit button in purchase_form")
            driver.execute_script(
                "var selection1=purchase_form.appendChild(document.createElement('section'));"
                "selection1.id='submit';")
        except:
            output_log(param.userFile, "Failure")
            output_log(param.userFile, "Generate subumit button in contents")
            driver.execute_script(
                "var selection1=contents.appendChild(document.createElement('section'));"
                "selection1.id='submit';")

        driver.execute_script(
            "document.getElementById('submit').setAttribute('class','center-btn fixed-btn');")
        driver.execute_script(
            "submit.appendChild(document.createElement('p'));")
        driver.execute_script(
            "submit.appendChild(document.createElement('p'));")
        driver.execute_script(
            "var p_tag3=submit.appendChild(document.createElement('p'));"
            "p_tag3.id='p_tag3';")
        driver.execute_script(
            "document.getElementById('p_tag3').setAttribute('class','button register center-block btn-procedure-pc-only');")
        driver.execute_script(
            "var submit_btn=p_tag3.appendChild(document.createElement('button'));"
            "submit_btn.id='submit_btn';"
            "submit_btn.innerText='お申込み / 購入手続き';")
        driver.execute_script(
            "document.getElementById('submit_btn').setAttribute('class','register_input_submit register_input_submit_pink');")
        driver.execute_script(
            "document.getElementById('submit_btn').setAttribute('data-role','none');")
        driver.execute_script(
            "document.getElementById('submit_btn').setAttribute('type','submit');")
        driver.execute_script(
            "document.getElementById('submit_btn').setAttribute('onclick','return buy_ticket()');")

    output_log(param.userFile, "end buy_ticket_overwrite_html")


# 時間付与してログ出力
def output_log(*str):
    print(datetime.datetime.now(), *str)


# if env.debugModeFlg:
#    main("user10.conf")
