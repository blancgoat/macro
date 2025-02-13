# coding=utf-8
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, expect

# constant
REFRESH_INTERVAL = 0

# param
param = {
    'id': 'id',
    'password': 'PassW@rd',
    'movie_url': 'https://www.cgv.co.kr/ticket/?MOVIE_CD_GROUP=20040028',
    'date': '20250215',  # yyyyMMdd
    'theater_area': '2',  # 상영관 지역 리스트에서 몇번째인지, 주로 2가 서울임
    'theater_cd': '0013',  # 상영관 코드
}

def setup_xhr_monitoring(page: Page):
    """XHR 모니터링을 위한 JavaScript 함수를 초기화합니다."""
    page.evaluate("""() => {
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
    }""")

def check_xhr_status(page: Page, second: int):
    """XHR 요청이 완료될 때까지 대기합니다."""
    last_zero_time = None

    while True:
        try:
            page.wait_for_function('() => window.activeXHRs === 0', timeout=10000)

            if last_zero_time is None:
                last_zero_time = time.time()
            elif time.time() - last_zero_time >= second:
                break
        except Exception:
            last_zero_time = None

        if page.evaluate('() => window.activeXHRs > 0'):
            last_zero_time = None

        page.wait_for_timeout(100)

def click_until_visible(page: Page, button_selector: str, visible_selector: str, timeout: int) -> bool:
    """버튼을 눌러서 특정 엘리먼트가 보일 때까지 클릭을 시도합니다."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            page.click(button_selector)
            if page.is_visible(visible_selector):
                return True
        except Exception:
            pass
        page.wait_for_timeout(100)
    return False

def try_login(page: Page) -> bool | float:
    """로그인을 시도하고 쿠키 만료 시간을 반환합니다."""
    page.goto('https://www.cgv.co.kr/user/login/default.aspx')

    if page.url == 'https://www.cgv.co.kr/user/login/default.aspx':
        page.fill('#txtUserId', param['id'])
        page.fill('#txtPassword', param['password'])
        page.click('#submit')

    return get_cookie_expiry_or_status(page)

def get_cookie_expiry_or_status(page: Page) -> float | int:
    """쿠키 상태를 확인합니다."""
    cookies = page.context.cookies()
    for cookie in cookies:
        if cookie.get('name') == 'cgv.cookie':
            return cookie.get('expires', True)
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,
                                    args=['--no-sandbox', '--disable-dev-shm-usage'],
                                    channel='chrome')
        page = browser.new_page()

        # 로그인
        expire_time = try_login(page)

        while True:
            try:
                # 예매 페이지 접근
                page.goto(param['movie_url'])
                frame_element = page.wait_for_selector('#ticket_iframe')
                frame = frame_element.content_frame()

                # XHR 모니터링 설정
                setup_xhr_monitoring(frame)
                check_xhr_status(frame, 2)

                # 극장 선택
                frame.click(f'#theater_area_list > ul > li:nth-child({param["theater_area"]})')
                frame.click(f'li[theater_cd="{param["theater_cd"]}"]')

                # 날짜 선택 및 새로고침
                is_not_while = False
                while not is_not_while:
                    page.wait_for_timeout(REFRESH_INTERVAL * 1000)

                    # 로그인 만료 체크
                    if expire_time is False or expire_time < time.time():
                        expire_time = try_login(page)
                        raise Exception(f'Session expired, try login again. Renewal time: {datetime.fromtimestamp(expire_time)}')

                    # 날짜 선택
                    frame.evaluate('window.initXHRCount()')
                    frame.click(f'li[date="{param["date"]}"]')

                    try:
                        frame.wait_for_function('() => window.activeXHRs === 0', timeout=2000)
                    except Exception:
                        print(f'ajax timeout, 차단가능성있음: {datetime.now()}')
                        continue

                    # 시간대 선택
                    time_button = frame.query_selector('.section-time li[data-index="0"]')
                    if time_button and 'disabled' not in (time_button.get_attribute('class') or ''):
                        time_button.click()
                        frame.click('#tnb_step_btn_right')
                        is_not_while = True
                        break

                # 좌석 선택 페이지
                frame.wait_for_selector('[class="step step2"]', state='visible')

                # # 나이제한 팝업 처리
                # frame.click('[class="ft_layer_popup popup_alert popup_previewGradeInfo ko"] .ft .btn_red')
                close_buttons = frame.query_selector_all('a.layer_close')
                for button in close_buttons:
                    try:
                        # 버튼이 보이는 경우에만 클릭
                        if button.is_visible():
                            button.click()
                    except:
                        continue

                # 인원 선택
                frame.click('#nop_group_adult li[data-count="1"]')

                # 좌석 선택
                try:
                    frame.click('#seats_list .seat:not([class*=" "])')
                except Exception as e:
                    print(f'시트선택 패배: {datetime.now()} : {e}')
                    continue

                # 결제 페이지 진입
                try:
                    success = click_until_visible(
                        frame,
                        '#tnb_step_btn_right.on',
                        '[class="step step3"]',
                        5
                    )
                    if not success:
                        raise Exception('Failed to proceed to payment page')
                except Exception as e:
                    print(f'결제진입 패배: {datetime.now()}: {e}')
                    continue

                break

            except Exception as e:
                print(f'무한 새로고침 while중 catch: {datetime.now()}: {e}')
                continue

        # 성공 알림
        os.system('say "떳다"')

        # 브라우저 유지
        page.wait_for_timeout(10000000)

if __name__ == "__main__":
    main()