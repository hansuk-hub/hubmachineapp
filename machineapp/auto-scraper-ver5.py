from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

import urllib.request
from bs4 import BeautifulSoup

from datetime import datetime

import random
import time
import os, sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import quote_plus
import re
from webdriver_manager.chrome import ChromeDriverManager


# from goto import goto, label



def waitTime(stayTime):
    if stayTime == 's':
        ranVal = random.randint(1, 1)
    else:
        ranVal = random.randint(1, 2)
    time.sleep(ranVal)


def mainLogin(firstCheck):
    if firstCheck == 0:
        driver.get('https://supplier.coupang.com/')
        driver.find_element_by_id('supplierId').send_keys('colamkt')
        driver.find_element_by_id('supplierPassword').send_keys('rymd02021**')
        waitTime('s')
        driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div/div[2]/div/div/div[5]/button').click()

        waitTime('s')

    try:
        # 페이지 갯수 알아내기
        driver.get(
            'https://supplier.coupang.com/scm/purchase/order/list?page=1&searchDateType=WAREHOUSING_PLAN_DATE&searchStartDate=' + getIndate + '&searchEndDate=' + getIndate + '&centerCode=&purchaseOrderSeq=&vendorPaymentInfoSeq=&purchaseOrderStatus=')
    except:  # 에러인 경우 한번 더 한다
        driver.get(
            'https://supplier.coupang.com/scm/purchase/order/list?page=1&searchDateType=WAREHOUSING_PLAN_DATE&searchStartDate=' + getIndate + '&searchEndDate=' + getIndate + '&centerCode=&purchaseOrderSeq=&vendorPaymentInfoSeq=&purchaseOrderStatus=')
    waitTime('s')
    waitTime('s')
    html = driver.page_source
#    print (html)

    soup = BeautifulSoup(html, 'html.parser')
    endPageNum = len(soup.select('#pagination ul li')) - 1

    print (endPageNum)

    ## 해당 입고일 발주서 URL 가져오기
    doc = client.open_by_url(
        'https://docs.google.com/spreadsheets/d/1MFc8cukd7Cir3ZpUl27MfIj1m3iEc7UiypDx3nsYpAA/edit#gid=0')
    waitTime('s')
    manageSheet = doc.worksheet('발주리스트관리')

    try:
        urlData = manageSheet.find(getIndate)
    except:
        print('발주 관리 리스트에 해당 날짜가 없습니다.')
        driver.close()
        sys.exit()

    global targetDateUrl

    # 발주 관리 시트의 마지막 줄을 알아온다.
    try :
        bulletinLastLine = len(manageSheet.col_values(1)) + 1
    except :
        bulletinLastLine = len(manageSheet.col_values(1)) + 1


    for i in range(2, bulletinLastLine, 1):
        if manageSheet.cell(i, 1).value == getIndate:
            targetDateUrl = manageSheet.cell(i, 2).value
            break
        else:
            targetDateUrl = "no data"

    if targetDateUrl == "no data":
        print("일치하는 날짜가 없어 프로그램 종료합니다.")
        driver.close()
        sys.exit()

    # 입고일 파일로 이동 후 작업시작
    doc = client.open_by_url(targetDateUrl)
    waitTime('s')

    for fi in range(1, endPageNum, 1):
        driver.get('https://supplier.coupang.com/scm/purchase/order/list?page=' + str(
            fi) + '&searchDateType=WAREHOUSING_PLAN_DATE&searchStartDate=' + getIndate + '&searchEndDate=' + getIndate + '&centerCode=&purchaseOrderSeq=&vendorPaymentInfoSeq=&purchaseOrderStatus=')

        print("Now page : " + str(fi))
        # 발주서 수량 카운트
        dealCount = driver.page_source
        dealCount = dealCount.count('콜라상회') - 1
        waitTime('s')

        # 발주서 박스 생성
        dealBox = []
        dealQty = []
        dealMoney = []
        dealCenter = []
        dealState = []

        # 발주리스트 페이지로 이동
        for fi in range(1, dealCount + 1, 1):
            getOrderNumber = driver.find_element_by_xpath(
                '/html[1]/body[1]/div[2]/div[2]/div[2]/div[4]/table[1]/tbody[1]/tr[' + str(fi) + ']/td[2]')  # 발주 번호
            getOrderCenter = driver.find_element_by_xpath(
                '/html[1]/body[1]/div[2]/div[2]/div[2]/div[4]/table[1]/tbody[1]/tr[' + str(fi) + ']/td[13]')  # 센터
            getOrderQty = driver.find_element_by_xpath(
                '/html[1]/body[1]/div[2]/div[2]/div[2]/div[4]/table[1]/tbody[1]/tr[' + str(fi) + ']/td[14]')  # 수량
            getOrderMoney = driver.find_element_by_xpath(
                '/html[1]/body[1]/div[2]/div[2]/div[2]/div[4]/table[1]/tbody[1]/tr[' + str(fi) + ']/td[16]')  # 금액
            getNowState = driver.find_element_by_xpath(
                '/html[1]/body[1]/div[2]/div[2]/div[2]/div[4]/table[1]/tbody[1]/tr[' + str(fi) + ']/td[5]')  # 발주 상태

            dealCenter.append(getOrderCenter.text)  # 센터 저장
            dealBox.append(getOrderNumber.text)  # 발주 번호 리스트 저장     # 지속된 오류로 코드 변경
            tempQty = int(str(getOrderQty.text).replace(",", ""))
            dealQty.append(tempQty)  # 발주 수량 저장
            dealMoney.append(getOrderMoney.text)  # 발주 금액 저장
            dealState.append(getNowState.text)  # 발주 상태 저장 - 발주 확정 요청 이외의 상황에서 -3 으로 변경해야한다.

        while True:
            try:
                BulletinSheet = doc.worksheet('Bulletin')
                break
            except:
                print("Bulletin Find Error - Don't Worry:")
                continue

        waitTime('s')

        now = str(datetime.now())[0:19]  # 시간저장

        ######### 해당 날짜의 발주 수량 대로 반복 5건의 반복이면 5번 반복
        for pageRoll in range(0, len(dealBox)):
            # driver.find_element_by_link_text(dealBox[pageRoll]).click()
            targetUrl = "https://supplier.coupang.com/scm/purchase/order/get/" + str(dealBox[pageRoll])
            driver.get(targetUrl)
            waitTime('s')
            curentUrlLink = driver.current_url  # 이동한 발주서 URL
            print(curentUrlLink)

            codeChk = 0  # 상품명과 바코드 저장시 토글읠 위한 변수
            barCodeBox = []  # 바코드 배열
            proNameBox = []  # 상품명 배열
            orderBox = []  # 주문 수량 배열
            proCodeBox = []  # 상품 코드 배열

            getCenter = dealCenter[pageRoll]
            print("Target Center : " + getCenter)

            # 바코드 및 상품명 저장
            spName = driver.find_elements_by_class_name('list-group-item')
            for item in spName:
                chkText = item.text
                if (chkText.find('회송됩니다.') > 1):
                    break
                if (item.text != '직매입') and (item.text != '과세'):
                    if codeChk == 0:
                        barCodeBox.append(item.text)  # 바코드 저장
                        codeChk = 1
                    else:
                        proNameBox.append(item.text)  # 상품명 저장
                        codeChk = 0

            # 상품 번호 저장
            pCode = driver.find_elements_by_class_name('sku-seq')
            for itemPcode in pCode:
                proCodeBox.append(itemPcode.text)

            # 주문 수량 저장
            # 주문 수량 위치는 1부터 시작되며 2씩 늘어난다.
            htmlCnt = driver.page_source
            soupCnt = BeautifulSoup(htmlCnt, 'html.parser')
            # print(soup)
            orderCnt = soupCnt.select('.scmTable.productInfo tbody tr .text-center.v-middle')
            for aaa in range(2, len(orderCnt) - 1, 4):
                orderBox.append(int(str(orderCnt[aaa].text).replace(",", "")))  # 수량 저장

            print("Order Number : " + str(dealBox[pageRoll]))
            while True:
                try:
                    curLastLine = len(BulletinSheet.col_values(1))
                    waitTime('s')
                    break
                except:
                    continue

            # 현황판에 발주 리스트 추가
            try:
                cell = BulletinSheet.find(str(dealBox[pageRoll]))
            except:
                while True:
                    try:
                        # print (getIndate, getCenter, dealBox[pageRoll], dealQty[pageRoll], dealMoney[pageRoll], curentUrlLink, now)
                        BulletinSheet.insert_row(
                            [getIndate, getCenter, dealBox[pageRoll], dealQty[pageRoll], dealMoney[pageRoll],
                             curentUrlLink, now],
                            curLastLine + 1)
                        break
                    except:
                        print("Bulletin Insert Error - Don't Worry:")
                        print(getIndate, getCenter, dealBox[pageRoll], dealQty[pageRoll], dealMoney[pageRoll],
                              curentUrlLink, now)
                        continue

            try:  # 시트를 선택하거나, 생성한다
                newSheet = doc.worksheet(getCenter)
            except:
                newSheet = doc.add_worksheet(title=getCenter, rows="1000", cols="20")

            printLine = 1

            while True:
                try:
                    # 마지막 줄 알아내기
                    stRow = len(newSheet.col_values(3))
                    # GD 해당 센터에서 해당발주번호가 있는지 찾는다
                    CenterDeal = newSheet.findall(str(dealBox[pageRoll]))
                    GDBarcodeRoom = []  # 취합된 GD의 바코드 배열

                    preOrderNum = ""
                    preBarcode = ""
                    break
                except:
                    continue



            # qtyCount = 0     # 해당 발주서의 수량 카운터

            # 0 이면, 해당 발주가 없므로 다 때려 넣는다.
            if (len(CenterDeal) == 0):
                print("기존 해당 센터에 데이터 없음으로 전체 " + str(len(barCodeBox)) + "개 데이터 입력...")

                for dateI in range(0, len(barCodeBox), 1):  # 입력 할 갯수 만큼 순환한다.
                    if (preOrderNum != dealBox[pageRoll]):  # 새로운 발주 번호 라면 무조건 찍는다.
                        preBarcode = proCodeBox[dateI]  # 이전 바코드 저장
                        preOrderNum = dealBox[pageRoll]  # 이전 발주 번호 저장
                        while True:
                            try:
                                print(str(dateI + 1), proCodeBox[dateI], proNameBox[dateI], '', str(getCenter),
                                      str(orderBox[dateI]), dealBox[pageRoll], str(getIndate))
                                # 상품명 라인 입력
                                newSheet.insert_row(
                                    [str(dateI + 1), proCodeBox[dateI], proNameBox[dateI], '', str(getCenter),
                                     str(orderBox[dateI]), dealBox[pageRoll], str(getIndate)], (printLine + stRow))
                                break
                            except:
                                continue

                        # 바코드 정보 라인 입력
                        while True:
                            try:
                                newSheet.insert_row(['', '', barCodeBox[dateI], "", "", "", str(now)],
                                                    printLine + 1 + stRow)
                                break
                            except:
                                continue
                        printLine = printLine + 2

                    # 같은 발주 번호에 같은 바코드라면 패스한다.
                    elif ((preBarcode != proCodeBox[dateI]) and (
                            dealBox[pageRoll] == preOrderNum)):  # 다른 발주번호에 다른 바코드 일때만 찍는다
                        preBarcode = proCodeBox[dateI]  # 이전 바코드 저장
                        preOrderNum = dealBox[pageRoll]  # 이전 발주 번호 저장
                        while True:
                            try:
                                print(str(dateI + 1), proCodeBox[dateI], proNameBox[dateI], '', str(getCenter),
                                      str(orderBox[dateI]), dealBox[pageRoll], str(getIndate))
                                # 상품명 라인 입력
                                newSheet.insert_row(
                                    [str(dateI + 1), proCodeBox[dateI], proNameBox[dateI], '', str(getCenter),
                                     str(orderBox[dateI]), dealBox[pageRoll], str(getIndate)], (printLine + stRow))
                                break
                            except:
                                continue

                        # 바코드 정보 라인 입력
                        while True:
                            try:
                                newSheet.insert_row(['', '', barCodeBox[dateI], "", "", "", str(now)],
                                                    printLine + 1 + stRow)
                                break
                            except:
                                continue
                        printLine = printLine + 2




            elif (len(CenterDeal) == len(barCodeBox)):
                print("이미 취합 완료된 발주서로 빠져 나갑니다.")


            else:  # 센터에 데이터가 있는 상황
                print("센터에 데이터가 있음... ")
                print(str(len(barCodeBox)) + "개 데이터 입력 예정...")

                preOrderNum = ""
                preBarcode = ""

                for CurData in CenterDeal:  # GD 의 해당 센터의 전체에 발주 번호를 가져온다.
                    getRow = CurData.row + 1
                    GDBarcodeRoom.append(newSheet.cell(getRow, 3).value)

                for MissData in range(0, len(barCodeBox)):
                    if barCodeBox[MissData] in GDBarcodeRoom:
                        print(barCodeBox[MissData] + " 이미 등록된 주문서 - 바코드 입니다")
                    else:

                        print("등록되지 않은 바코드 추가합니다.")

                        ##############################################################################################################

                        if (preOrderNum != dealBox[pageRoll]):  # 새로운 발주 번호 라면 무조건 찍는다.
                            preBarcode = proCodeBox[MissData]  # 이전 바코드 저장
                            preOrderNum = dealBox[pageRoll]  # 이전 발주 번호 저장
                            while True:
                                try:
                                    print(str(MissData + 1), proCodeBox[MissData], proNameBox[MissData], '',
                                          str(getCenter),
                                          str(orderBox[MissData]), str(dealBox[pageRoll]), str(getIndate))
                                    # 상품명 라인 입력

                                    newSheet.insert_row(
                                        [str(MissData + 1), proCodeBox[MissData], proNameBox[MissData], '',
                                         str(getCenter),
                                         str(orderBox[MissData]), str(dealBox[pageRoll]), str(getIndate)],
                                        printLine + stRow)
                                    break
                                except:
                                    continue

                            # 바코드 정보 라인 입력
                            while True:
                                try:
                                    newSheet.insert_row(['', '', barCodeBox[MissData], "", "", "", str(now)],
                                                        printLine + 1 + stRow)
                                    break
                                except:
                                    continue
                            printLine = printLine + 2

                        # 같은 발주 번호에 같은 바코드라면 패스한다.
                        elif ((preBarcode != proCodeBox[MissData]) and (
                                dealBox[pageRoll] == preOrderNum)):  # 다른 발주번호에 다른 바코드 일때만 찍는다
                            preBarcode = proCodeBox[MissData]  # 이전 바코드 저장
                            preOrderNum = dealBox[pageRoll]  # 이전 발주 번호 저장
                            while True:
                                try:
                                    print(str(MissData + 1), proCodeBox[MissData], proNameBox[MissData], '',
                                          str(getCenter),
                                          str(orderBox[MissData]), str(dealBox[pageRoll]), str(getIndate))  # 상품명 라인 입력
                                    newSheet.insert_row(
                                        [str(MissData + 1), proCodeBox[MissData], proNameBox[MissData], '',
                                         str(getCenter),
                                         str(orderBox[MissData]), str(dealBox[pageRoll]), str(getIndate)],
                                        printLine + stRow)
                                    break
                                except:
                                    continue

                            # 바코드 정보 라인 입력
                            while True:
                                try:
                                    newSheet.insert_row(['', '', barCodeBox[MissData], "", "", "", str(now)],
                                                        printLine + 1 + stRow)
                                    break
                                except:
                                    continue
                            printLine = printLine + 2

            ################################################################################################

            # while True :
            #      try :      #상품명 라인 추가
            #          newSheet.insert_row(
            #          [str(MissData + 1), proCodeBox[MissData], proNameBox[MissData], '', str(getCenter),
            #           str(orderBox[MissData]), str(dealBox[pageRoll]), str(getIndate)], printLine +stRow)
            #          break
            #      except : continue
            #
            # while True :
            #     try :    #바코드 라인 추가
            #         newSheet.insert_row(['', '', barCodeBox[MissData], "", "", "", str(now)], printLine + 1 + stRow)
            #         break
            #     except :  continue
            #
            # printLine = printLine + 2

            print("\n")

            driver.execute_script("window.history.go(-1)")
            waitTime('s')

    print("작업이 완료 되었습니다.")


def run_main():
    # 발주 관리 리스트
    # https://docs.google.com/spreadsheets/d/1MFc8cukd7Cir3ZpUl27MfIj1m3iEc7UiypDx3nsYpAA/edit#gid=0

    api = 'gspread.json'

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(api, scope)
    client = gspread.authorize(creds)

    ##########################################################################################

    while (1):
        # getIndate = str(quote_plus(input("취합 원하는 입고일은 ? ex)2020-03-15 : ")))
        # chkString = re.compile("\d{4}[\s-]?\d{2}[-]?\d{2}")
        # chkString = chkString.findall(getIndate)

        # if chkString and (len(getIndate) == 10):
        #    print(str(chkString) + " 데이터를 취합 시작 합니다.")
        #    break
        # else:
        #    print("날짜를 다시 입력하세요")
        getIndate = '2021-08-05'
        break
    #############################################################################################

    # driver: WebDriver = webdriver.Chrome(r'C:\work\python\auto-worker\coupang\venv\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    # chrome_driver_path = './'

    # driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    driver = webdriver.Chrome(chrome_options=options, executable_path="/home/ubuntu/chromedriver")


    firstCheck = 0

    mainLogin(firstCheck)
    # while True :
    #     try :
    #         mainLogin( firstCheck )
    #         break
    #     except :
    #         print("Unexpected error:", sys.exc_info()[0])
    #         firstCheck += 1
    #         continue

    driver.close()

