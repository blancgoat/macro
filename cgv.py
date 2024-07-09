# coding=utf-8
import time
import os
from datetime import datetime

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

# param
id = "id"
password = "PassW@rd"
movieUrl = "https://www.cgv.co.kr/ticket/?MOVIE_CD=20037219&MOVIE_CD_GROUP=20036657"
date = "20240720" # yyyyMMdd
theater_cd = "0013" # 상영관 코드

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.implicitly_wait(4)
driver.get("https://www.cgv.co.kr/user/login/default.aspx")
driver.find_element(By.ID, "txtUserId").send_keys(id)
driver.find_element(By.ID, "txtPassword").send_keys(password)
driver.find_element(By.ID, "submit").click()
# 로그인 완료

while True:
    driver.get(movieUrl)
    driver.switch_to.frame("ticket_iframe")
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, f'li[theater_cd="{theater_cd}"]').click()
    time.sleep(2)
    dateButton = driver.find_element(By.CSS_SELECTOR, f'li[date="{date}"]')

    driver.execute_script("""
        window.activeXHRs = 0;
        window.initXHRCount = function() {
            window.activeXHRs = 0;
        };
        (function(open) {
            XMLHttpRequest.prototype.open = function() {
                window.activeXHRs++;
                this.addEventListener('loadend', function() {
                    window.activeXHRs--;
                });
                open.apply(this, arguments);
            };
        })(XMLHttpRequest.prototype.open);
    """)

    # 무한 새로고침 while # TODO 간헐적으로 프론트동작이이상함 해당스케줄에 영화관이없다는 알럿이 나올때가있음 이는 ajax에서 에러났는데 200처리된것으로 예상됨 프론트오류나면 전체로직을 continue할 필요있을듯
    isNotWhile = False
    while not isNotWhile:
        time.sleep(0.5)
        driver.execute_script("window.initXHRCount();")
        wait.until(EC.element_to_be_clickable(dateButton)).click()
        try:
            wait.until(lambda d: d.execute_script("return window.activeXHRs === 0"))
        except TimeoutException:
            print("타임아웃 발생")
            continue

        for i in range(0, 5):
            button = driver.find_element(By.CLASS_NAME, "section-time").find_element(By.CSS_SELECTOR, f'li[data-index="{i}"]')
            isNotWhile = button.get_attribute("class") != "disabled"
            if isNotWhile:
                button.click()
                driver.find_element(By.ID, "tnb_step_btn_right").click()
                break
    # 진입성공
    # 나이제한 팝업 TODO 이거뜰때도있고 안뜰때있는거처리 및 우선순위 낮출필요있음[해당 처리로직동안 순위밀림]
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, '[class="ft_layer_popup popup_alert popup_previewGradeInfo ko"] .ft .btn_red')
    )).click()

    # 성인한명 클릭
    driver.find_element(By.ID, "nop_group_adult").find_element(By.CSS_SELECTOR, f'li[data-count="1"]').click()

    # 시트 클릭
    try:
        driver.find_element(By.ID, "seats_list").find_element(By.CSS_SELECTOR, ".seat:not([class*=' '])").click()
    # 들어왔는데 seat가 없을수도있음
    except NoSuchElementException as e:
        print(f"패배: {e}: {datetime.now()}")
        continue

    # 결제페이지 진입
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tnb_step_btn_right.on"))).click()
    # 시트선택까진했으나 결제진입단계에서 패배
    except UnexpectedAlertPresentException as e:
        print(f"패배: {e}: {datetime.now()}")
        continue

    break

os.system('say "떳다"')

while True:
    time.sleep(10)
