# coding=utf-8
import time
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By


# constant
REFRESH_INTERVAL = 0
DRIVER = webdriver.Chrome()
WAIT = WebDriverWait(DRIVER, 10)

# param
param = {
    'url': 'https://reserve.cwsisul.or.kr/ollec/cwsisul/lec_view.do?idx_id=100016',
}


'''로그인'''
DRIVER.implicitly_wait(4)
DRIVER.get('https://reserve.cwsisul.or.kr/ollec/cwsisul/login.do')
DRIVER.find_element(By.ID, 'naverIdLogin_loginButton').click()
# 직접로그인 #
WebDriverWait(DRIVER, 1000).until(lambda DRIVER: 'https://reserve.cwsisul.or.kr/ollec/cwsisul/intro.do' in DRIVER.current_url)

DRIVER.get(param['url'])
while True:
    parent = DRIVER.find_element(By.CLASS_NAME, 'lec_tit_r')
    if not parent.get_attribute('innerHTML').strip():
        sleep(0.5)
        DRIVER.refresh()
        continue

    try:
        WebDriverWait(DRIVER, 1000).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn_reg'))
        ).click()
        break
    except (TimeoutException, StaleElementReferenceException) as e:
        print(f"클릭 시도 실패: {str(e)}")

checkboxes = WAIT.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form[name='agree'] input[type='checkbox']"))
)

for checkbox in checkboxes:
    WAIT.until(EC.element_to_be_clickable(checkbox))
    if not checkbox.is_selected():
        checkbox.click()

WAIT.until(EC.element_to_be_clickable(DRIVER.find_element(By.CLASS_NAME, 'btn_reg'))).click()
WAIT.until(EC.element_to_be_clickable(DRIVER.find_element(By.ID, 'btn_submit'))).click()


os.system('say "떳다"')
while True:
    time.sleep(10)
