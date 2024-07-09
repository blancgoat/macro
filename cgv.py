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

    # 무한 새로고침 while #
    try:
        isNotWhile = False
        while not isNotWhile:
            time.sleep(0.5)
            driver.execute_script("window.initXHRCount();")
            wait.until(EC.element_to_be_clickable(dateButton)).click()
            try:
                wait.until(lambda d: d.execute_script("return window.activeXHRs === 0"))
            except TimeoutException:
                print(f"ajax timeout 발생, 차단가능성있음: {datetime.now()}")
                continue

            # 여기서 시간대 선택이 가능함, 단순하게 설계하긴했으나 시제품이아닌이상 굳이..
            for i in range(0, 5):
                button = driver.find_element(By.CLASS_NAME, "section-time").find_element(By.CSS_SELECTOR, f'li[data-index="{i}"]')
                isNotWhile = button.get_attribute("class") != "disabled"
                if isNotWhile:
                    wait.until(EC.element_to_be_clickable(button)).click()
                    driver.find_element(By.ID, "tnb_step_btn_right").click()
                    break
    except UnexpectedAlertPresentException as e:
        print(f"왜 알럿발생을하지: {e}: {datetime.now()}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        finally:
            continue
    except Exception as e:
        print(f"뭔 에러여: {e}: {datetime.now()}")
        continue

    # 진입성공 #
    # step2 페이지가 visiable 됬는지 확인
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="step step2"]')))

    # 여러가지상황에(나이제한팝업등) 따라 blackscreen 이 발생할 수 있다. 모든상황에서 blackscreen을 제거
    blackscreen = driver.find_element(By.ID, "blackscreen")
    if blackscreen.is_displayed():
        driver.execute_script("arguments[0].style.display = 'none';", blackscreen)

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
    submitButton = driver.find_element(By.ID, "tnb_step_btn_right")
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tnb_step_btn_right.on"))).click()
    # 시트선택까진했으나 결제진입단계에서 패배
    except UnexpectedAlertPresentException as e:
        print(f"패배: {e}: {datetime.now()}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        finally:
            continue

    break

# 나이제한 팝업
try:
    redButton = driver.find_element(By.CSS_SELECTOR, '[class="ft_layer_popup popup_alert popup_previewGradeInfo ko"] .ft .btn_red')
    if redButton.is_displayed() and redButton.is_enabled():
        redButton.click()
except NoSuchElementException:
    pass
except : # 개억까 방지용 결제페이지가 눈앞에있는데 별거아닌걸로 브라우저 닫히면 자살할듯
    pass

os.system('say "떳다"')

while True:
    time.sleep(10)
