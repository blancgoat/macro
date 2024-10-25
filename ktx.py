# coding=utf-8
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
limit: int = 1 # min is 1
isSloppy: bool = False # 입석+좌석 도 선택할지 여부, false면 입석+좌석은 선택하지않음

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
i = 0

while True:
    i += 1

    if i == limit + 1:
        i = 1
        time.sleep(1)
        driver.refresh()

    try:
        ele = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, f"//table[@id='tableResult']//tbody/tr[{i}]/td[6]"))
        )

        if len(ele.find_elements(By.XPATH, ".//*")) == 1:
            print(str(i) + "매진")
            continue
        else:
            try:
                ele.find_element("name", "btnRsv1_" + str(i - 1)).click()
            except NoSuchElementException:
                if isSloppy:
                    ele.find_element("name", "btnRsv8_" + str(i - 1)).click()
                else:
                    print(str(i) + "입좌석스킵")
                    continue
            break
    except NoSuchElementException:
        print("nope")
        print(i)
        os.system('say "문제가 발생했을수도 있으니, 크롬엔진은 확인하여 주세요."')
        continue
    except TimeoutException:
        print(f"30초 동안 요소를 찾지 못했습니다: tr[{i}]/td[6]")
        continue

# 안내메세지 팝업뜰때가 있는데 그때 처리용
time.sleep(1)
try:
    driver.switch_to.frame("embeded-modal-traininfo")
    driver.find_elements(By.CLASS_NAME, "pop_close")[0].click()
except NoSuchElementException:
    pass

os.system('say "케이티엑스 발권이 완료되었습니다. 결제를 진행하여 주세요."')
while True:
    print("대기중")
    time.sleep(10)