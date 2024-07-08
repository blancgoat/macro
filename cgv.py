# coding=utf-8
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
import os

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
x = driver.find_element(By.CSS_SELECTOR, f'li[date="{date}"]')
x.click()
time.sleep(2)

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
while not isNotWhile:
    time.sleep(1)
    driver.execute_script("window.initXHRCount();")
    x.click()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return window.activeXHRs === 0")
    )

    for i in range(2, 5):
        button = driver.find_element(By.CLASS_NAME, "section-time").find_element(By.CSS_SELECTOR, f'li[data-index="{i}"]')
        isNotWhile = button.get_attribute("class") != "disabled"
        if isNotWhile:
            button.click()
            driver.find_element(By.ID, "tnb_step_btn_right").click()
            break

driver.implicitly_wait(4)
driver.switch_to.frame("proxy_iframe")
driver.find_element(By.CLASS_NAME, "btn btn_ok btn_red").click()
driver.switch_to.default_content()
driver.find_element(By.ID, "nop_group_adult").find_element(By.CSS_SELECTOR, f'li[data-count="1"]').click()

os.system('say "떳다"')

while True:
    time.sleep(10)
