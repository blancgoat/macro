# coding=utf-8
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import os

# param
memberShipNo = "1234512345"
password = "P@ssw0rd"
startingPoint = "서울"
endingPoint = "강릉"
day: str = "4"
hour: str = "10"
month: str = "2"
year: str = "2023"
limit: int = 2 # min is 2

driver = webdriver.Chrome()
driver.implicitly_wait(4)
driver.get("https://www.letskorail.com/korail/com/login.do")
driver.find_element("name", "txtMember").send_keys(memberShipNo)
driver.find_element("name", "txtPwd").send_keys(password)
driver.find_element("xpath", "//img[@src ='/images/btn_login.gif']").click()


driver.switch_to.window(driver.window_handles[0])

driver.get("https://www.letskorail.com/ebizprd/EbizPrdTicketpr21100W_pr21110.do")
driver.find_element("id", "selGoTrainRa00").click()
txtGoStart = driver.find_element("name", "txtGoStart")
txtGoStart.clear()
txtGoStart.send_keys(startingPoint)

txtGoEnd = driver.find_element("name", "txtGoEnd")
txtGoEnd.clear()
txtGoEnd.send_keys(endingPoint)

if year is not None:
    driver.find_element("name", "selGoYear").send_keys(year)
if month is not None:
    driver.find_element("name", "selGoMonth").send_keys(month)
if day is not None:
    driver.find_element("name", "selGoDay").send_keys(day)
if hour is not None:
    driver.find_element("name", "selGoHour").send_keys(hour)

driver.find_elements(By.CLASS_NAME, "btn_inq")[0].click()

time.sleep(1)
i = 1

while True:
    if i == limit:
        i = 1
        time.sleep(1)
        driver.refresh()

    try:
        ele = driver.find_element(By.ID, "tableResult").find_element(By.XPATH, "//tbody/tr[" + str(i) + "]/td[6]")

        if len(ele.find_elements(By.XPATH, ".//*")) == 1:
            print(str(i) + "매진")
            i += 1
            continue
        else:
            ele.find_element("name", "btnRsv1_" + str(i - 1)).click()
            os.system('say "케이티엑스 발권이 완료되었습니다. 결제를 진행하여 주세요."')
            break
    except NoSuchElementException:
        print("nope")
        print(i)
        os.system('say "문제가 발생했을수도 있으니, 크롬엔진은 확인하여 주세요."')
        continue


while True:
    print("대기중")
    time.sleep(1)