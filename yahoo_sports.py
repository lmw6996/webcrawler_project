import random
import time
from selenium import webdriver  # Selenium 웹드라이버 핵심 모듈
from selenium.webdriver.common.by import By # HTML 요소를 찾을 때 사용하는 선택자 타입
from selenium.webdriver.support.ui import WebDriverWait # 특정 요소가 나타날 때까지 기다리기 위한 도구
from selenium.webdriver.support import expected_conditions as EC # 요소 클릭 가능, 존재 여부 등 대기 조건 정의
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager # ChromeDriver를 자동으로 설치 및 관리하기 위한 라이브러리
from selenium.common.exceptions import TimeoutException  #예외 처리용

# Driver 생성 및 기본 옵션 설정
def create_driver():
    options = Options()
    options.add_argument("--start-maximized") # 사용자 행동처럼 보이도록 브라우저를 최대화된 상태로 실행 
    options.add_argument("--disable-blink-features=AutomationControlled") # Selenium 자동화 탐지 우회
    options.page_load_strategy = "eager" #속도 향상
    
    # ChromeDriver 자동 관리
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# 1. Yahoo Sports 접속 
def open_yahoosports_main(driver):
    print("1. Yahoo Sports 접속")
    driver.get("https://sports.yahoo.com/") # Yahoo Sports 메인 페이지 이동
    time.sleep(2) #페이지 로딩 대기

# 2. 스포츠 종목 랜덤 선택 
def click_category(driver):
    print("2. 스포츠 종목 랜덤 선택")
    sports = (
        "https://sports.yahoo.com/nfl/",
        "https://sports.yahoo.com/ncaaf/",
        "https://sports.yahoo.com/nba/",
        "https://sports.yahoo.com/ncaab/",
        "https://sports.yahoo.com/ncaaw/",
        "https://sports.yahoo.com/mlb/",
        "https://sports.yahoo.com/wnba/"    
    )  # 주요 스포츠 종목 URL 목록

    driver.get(random.choice(sports)) # 하나 랜덤으로 선택하여 이동
    time.sleep(3)

# 3. 종목 News 탭 클릭
def click_news_tab(driver):
    print("3. 종목 News 탭 클릭 시도")
    wait = WebDriverWait(driver, 3)   # 최대 3초까지 요소 대기

    try:
         # News 텍스트를 가진 탭 요소를 찾아 클릭 가능 상태가 될 때까지 대기
        news_tab= wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[normalize-space()='News']/ancestor::a") #xpath는 ui 변경에 강함
            )
        )
        news_tab.click() # News 탭 클릭
        time.sleep(3) #로딩 대기
   
    except TimeoutException: #news 탭 없을 떄 종료하도록
        print("News 탭을 찾을 수 없음.")

# 4. 스크롤하며 기사 URL 수집 
def scroll_news_page(driver):
    print("4. 기사 목록 스크롤 및 기사 URL 수집")
    c= set()  # 중복 제거를 위한 집합

    for _ in range(3): # 페이지 스크롤
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1.5)

        #뉴스 기사만 잡아내기 위해 여러가지 조건 걸었다
        urls = driver.execute_script("""
            const links = [];
            document.querySelectorAll('a').forEach(a => {
                const href = a.href || '';
                if (
                    href.includes('sports.yahoo.com') &&
                    (href.includes('/article/') || href.match(/-\d{8,}\.html/)) &&
                    !href.includes('/watch/') &&  
                    !href.includes('/fantasy/')
                ) {
                    links.push(href);
                }
            });
            return links;
        """)
        for u in urls:
            c.add(u) # 중복 제거하고 저장
    return list(c)

# 5. 기사 클릭
def click_news(driver, article_urls):
    if not article_urls:
        return False

    article_url = random.choice(article_urls) #수집한 후보중 하나 랜덤 방문
    print("5. 기사 랜덤 선택 및 본문 이동")

    driver.get(article_url)
    time.sleep(3)
    return True

# 6. 기사 본문 스크롤
def read_post_with_scroll(driver):
    print("6. 기사 본문 스크롤")
    for _ in range(8):
        driver.execute_script(
            f"window.scrollBy(0, 400);"   # 한 번에 400px씩 아래로 이동
        )
        time.sleep(0.8)     
    print("기사 읽기 완료")

# main
def main():
    driver = create_driver() # Selenium 드라이버 생성
    try:
        open_yahoosports_main(driver)
        click_category(driver)
        click_news_tab(driver) 
        article_urls = scroll_news_page(driver)
        
        if click_news(driver, article_urls):
            read_post_with_scroll(driver)
        else:
            print("프로세스 중단: 기사 못 찾음")

        time.sleep(3)
   
    except Exception as e:
        print(f"오류 발생: {e}")  # 예외 발생 시 로그 출력
   
    finally:
        driver.quit()
        print("크롤링 종료")

if __name__ == "__main__":
    main()