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

driver.implicitly_wait(4)
driver.get("https://www.cgv.co.kr/user/login/default.aspx")
driver.find_element(By.ID, "txtUserId").send_keys(id)
driver.find_element(By.ID, "txtPassword").send_keys(password)
driver.find_element(By.ID, "submit").click()
# 로그인 완료

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

isNotWhile = False
wait = WebDriverWait(driver, 10)
while not isNotWhile:
    time.sleep(0.5)
    driver.execute_script("window.initXHRCount();")
    wait.until(EC.element_to_be_clickable(dateButton)).click()
    try:
        wait.until(
            lambda d: d.execute_script("return window.activeXHRs === 0")
        )
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

wait.until(EC.element_to_be_clickable((
    By.CSS_SELECTOR, '[class="ft_layer_popup popup_alert popup_previewGradeInfo ko"] .ft .btn_red')
)).click()

driver.find_element(By.ID, "nop_group_adult").find_element(By.CSS_SELECTOR, f'li[data-count="1"]').click()
try:
    driver.find_element(By.ID, "seats_list").find_element(By.CSS_SELECTOR, ".seat:not([class*=' '])").click() # 들어왔는데 seat가 없을수도있음
except NoSuchElementException as e:
    print(f"패배: {e}: {datetime.now()}")

try:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tnb_step_btn_right.on"))).click()
except UnexpectedAlertPresentException as e:
    print(f"패배: {e}: {datetime.now()}")

os.system('say "떳다"')

while True:
    time.sleep(10)
