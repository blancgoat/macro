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
from selenium.webdriver.remote.webelement import WebElement

# param
id = "id"
password = "PassW@rd"
movie_url = "https://www.cgv.co.kr/ticket/?MOVIE_CD=20037219&MOVIE_CD_GROUP=20036657"
date = "20240720" # yyyyMMdd
theater_cd = "0013" # 상영관 코드

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def initialize_xhr_monitoring():
    """XHR 갯수파악 함수를 초기화합니다. activeXHRs 라는 변수명을 공유하기 위해 함수로 사용"""
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

def check_xhr_status(second: int):
    """
    second까지 pending XHR이 전부 사라지는지 확인합니다.
    second까지는 무조건 대기하고있는게 특징입니다. XHR이 pending인게 계속 있다면 무한루프가 발생할 수 도 있습니다.
    cgv가 첫 document로드시 스크립트가 스크립트를 호출하면서 진행되는데 중간에 dom load가 완료되는것으로 보여 해당함수를 작성하였습니다.
    정확히는 element가 아닌 XHR를 보기때문에 정확하진 않을수있으나 완료를 기준으로할 element가 뭔지 알 수 없기에 XHR기준으로 설계했습니다.
    """
    last_zero_time = None

    while True:
        try:
            wait.until(lambda d: d.execute_script("return window.activeXHRs === 0"))

            if last_zero_time is None:
                last_zero_time = time.time()
            elif time.time() - last_zero_time >= second:
                break
        except TimeoutException:
            last_zero_time = None

        if driver.execute_script("return window.activeXHRs > 0"):
            last_zero_time = None

        time.sleep(0.1)

def click_until_change(button_element: WebElement, target_element: WebElement, timeout: int = 30) -> bool:
    """
    버튼을 눌러서 타켓엘레먼트가 변경될때까지 계속 클릭해주는 함수
    :param button_element:
    :param target_element:
    :param timeout:
    :return: 변경성공시 Ture, Timeout까지 변경실패시 False
    """
    original_content = target_element.text

    def element_changed():
        return target_element.text != original_content

    start_time = time.time()
    while time.time() - start_time < timeout:
        button_element.click()
        try:
            WebDriverWait(button_element.parent, 1).until(lambda _: element_changed())
            return True
        except TimeoutException:
            continue

    return False


'''로그인'''
driver.implicitly_wait(4)
driver.get("https://www.cgv.co.kr/user/login/default.aspx")
driver.find_element(By.ID, "txtUserId").send_keys(id)
driver.find_element(By.ID, "txtPassword").send_keys(password)
driver.find_element(By.ID, "submit").click()

while True:
    '''얘매페이지 접근'''
    driver.get(movie_url)
    iframe = wait.until(EC.presence_of_element_located((By.ID, "ticket_iframe")))
    driver.switch_to.frame(iframe)

    initialize_xhr_monitoring()
    '''
    url을 통해 ready류 script가 동작하는것같은데 이게 script가 다시 script를 호출하는 방식이라서
    한번 done상태가됨 그래서 1초이내에 xhr이 pending 이 유지되고있는지 확인하는식으로 처리
    사실 이렇게 복잡하게 할필요없고 쿨하게 time.sleep걸어주는게 현명할것같다.
    '''
    check_xhr_status(2)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[theater_cd="{theater_cd}"]'))).click()

    date_button = driver.find_element(By.CSS_SELECTOR, f'li[date="{date}"]')
    step_frame2 = driver.find_element(By.CSS_SELECTOR, '[class="step step2"]')
    step_frame3 = driver.find_element(By.CSS_SELECTOR, '[class="step step3"]')

    '''무한 새로고침 while'''
    try:
        is_not_while = False
        while not is_not_while:
            time.sleep(0.5)
            driver.execute_script("window.initXHRCount();")
            wait.until(EC.element_to_be_clickable(date_button)).click()
            try:
                wait.until(lambda d: d.execute_script("return window.activeXHRs === 0"))
            except TimeoutException:
                print(f"ajax timeout 발생, 차단가능성있음: {datetime.now()}")
                continue

            # 여기서 시간대 선택이 가능함, 단순하게 설계하긴했으나 시제품이아닌이상 굳이..
            for i in range(0, 5):
                button = driver.find_element(By.CLASS_NAME, "section-time").find_element(By.CSS_SELECTOR, f'li[data-index="{i}"]')
                is_not_while = button.get_attribute("class") != "disabled"
                if is_not_while:
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

    '''진입성공'''
    # step2 페이지가 visiable 됬는지 확인
    wait.until(EC.visibility_of(step_frame2))

    # 나이제한 팝업제거
    # 해당팝업로드 기다리면서 왠만한 프론트로직이 로드완료됨 이쪽이 훨씬 안정성이 좋아 해당 코드를 부활
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, '[class="ft_layer_popup popup_alert popup_previewGradeInfo ko"] .ft .btn_red')
    )).click()

    # 성인한명 클릭
    driver.find_element(By.ID, "nop_group_adult").find_element(By.CSS_SELECTOR, f'li[data-count="1"]').click()

    # 시트 클릭
    try:
        driver.find_element(By.ID, "seats_list").find_element(By.CSS_SELECTOR, ".seat:not([class*=' '])").click()
    # 간혹 활성화시트가없는데도 들어와지는 케이스가존재
    except Exception as e:
        print(f"시트선택 패배: {e}: {datetime.now()}")

    # 결제페이지 진입
    try:
        '''
        clickable이랑 css변경체크까지 확인해도 함수가 동작은하는데 아무동작안하는 함수일때도있다.
        아마 특정 form값 변경을 만족해야하는것 같은데 그값이 뭔지 알방법이없다.
        어쩔수없이 step3로 이동할때까지 무한클릭하는 함수를 적용했다
        '''
        click_until_change(
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tnb_step_btn_right.on"))),
            step_frame3
        )
    # 시트선택까진했으나 결제진입단계에서 패배
    except UnexpectedAlertPresentException as e:
        print(f"결제진입 패배: {e}: {datetime.now()}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        finally:
            continue

    break

os.system('say "떳다"')

while True:
    time.sleep(10)
