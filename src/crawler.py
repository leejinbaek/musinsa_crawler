from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import csv
import traceback
import time


# 초기 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 페이지 스크롤 함수
def page_down(num):
    section = driver.find_element(By.TAG_NAME, "body")
    for i in range(num):
        section.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.01)
        

# 메인
def crawler():
    try:
        print("해당 크롤러는 무신사 상품의 인기 상품들을 순서대로 보여줍니다.")
        print("최근 3개월간의 판매량을 기준으로 데이터를 수집합니다.")
        category = {
        "상의" : "001",
        "아우터" : "002",
        "바지" : "003",
        "원피스" : "020",
        "신발" : "018",
        "가방" : "004",
        "패션소품" : "007",
        "언더웨어" : "026",
        "뷰티" : "015",
        "라이프": "012" 
        }
        while True:
            keyword = input("상의, 바지, 아우터, 원피스, 신발, 가방, 패션소품, 언더웨어, 뷰티, 라이프 중 한 가지 키워드를 입력하세요: ")
            #키워드 이쪽에 넣기
            if keyword in category:
                url = f"https://www.musinsa.com/categories/item/{category[keyword]}?device=mw&sortCode=3m"
                break
            else:
                print("키워드가 올바르지 않습니다. 다시 입력해주세요")
                
        #카테고리에 맞는 url로 이동
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'category__sc-')]")))
        
        #로딩 대기
        search_era = driver.find_element(By.XPATH, "//div[contains(@class, 'category__sc-')]")
        if search_era != driver.find_element(By.XPATH, "//div[contains(@class, 'category__sc-')]"):
            raise ValueError("search_era not found")
        
        #페이지 스크롤
        page_down(100)
        
        #soup 생성
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
    
        #저장공간 생성
        clothes_db = []
        
        #페이지 크롤링
        clothes = soup.find_all("div" , class_="category__sc-rb2kzk-10 cjDxkP")
        for cs in clothes:
            shop = cs.find("a", class_="category__sc-rb2kzk-11 kPDCPR").text
            name = cs.find("a", class_="category__sc-rb2kzk-12 gBkfRU").text
            og_price = None
            og_price = cs.find("del", class_="category__sc-79f6w4-6 iHtcSg")
            if og_price is not None:
                og_price = og_price.text
            dc = None
            dc = cs.find("strong", class_="category__sc-79f6w4-9 jNpLBZ")
            if dc is not None:
                dc = dc.text
            
            price = cs.find("span", class_="category__sc-79f6w4-5 eTRmwC").text
            
            clothes_data = {
                "shop" : shop,
                "name" : name,
                "og_price" : og_price,
                "dc" : dc,
                "price" : price
            }
            clothes_db.append(clothes_data)
    
        print(clothes_db)
    
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
    
    finally:
        print("크롤러 종료")
        driver.quit()

crawler()