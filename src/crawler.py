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
options.add_argument("headless")
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
        
##페이지 크롤링 함수
def page_crawling(driver,limit, max_item_InList):
    #저장공간 생성
    clothes_db = []
    
    #seendata 생성
    seen_data = set()
    
    #scroll_limit 설정
    scroll_limit = 0
    
    while scroll_limit < limit and len(clothes_db) < max_item_InList:
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        page_down(1)
        
        #페이지 크롤링
        clothes = soup.find_all("div" , class_="category__sc-rb2kzk-10 cjDxkP")
        for cs in clothes:
            shop = None
            shop = cs.find("a", class_="category__sc-rb2kzk-11 kPDCPR")
            if shop is not None:
                shop = cs.find("a", class_="category__sc-rb2kzk-11 kPDCPR").text
                
            name = None
            name = cs.find("a", class_="category__sc-rb2kzk-12 gBkfRU")
            if name is not None:
                name = cs.find("a", class_="category__sc-rb2kzk-12 gBkfRU").text
                
            og_price = None
            og_price = cs.find("del", class_="category__sc-79f6w4-6 iHtcSg")
            if og_price is not None:
                og_price = og_price.text
                
            dc = None
            dc = cs.find("strong", class_="category__sc-79f6w4-9 jNpLBZ")
            if dc is not None:
                dc = dc.text
                
            price = None
            price = cs.find("span", class_="category__sc-79f6w4-5 eTRmwC")
            if price is not None:
                price = cs.find("span", class_="category__sc-79f6w4-5 eTRmwC").text
            
            sold_out = None
            sold_out = cs.find("a", class_="category__sc-rb2kzk-11 WUSGE")
            if sold_out is not None:
                sold_out = "품절"
            else:
                sold_out = "재고 있음"
            
            clothes_data = {
                "shop" : shop,
                "name" : name,
                "og_price" : og_price,
                "dc" : dc,
                "price" : price,
                "sold_out" : sold_out
            }
            clothes_data_tuple = tuple(clothes_data.items())
            if clothes_data_tuple not in seen_data:
                seen_data.add(clothes_data_tuple)
                clothes_db.append(clothes_data)
            
            if len(clothes_db) >= max_item_InList:
                break
        scroll_limit += 1
        
    return clothes_db

# 메인
def crawler():
    try:
        print("해당 크롤러는 무신사 상품의 인기 상품들을 순서대로 보여줍니다.")
        category = {
        "상의" : "001",
        "아우터" : "002",
        "바지" : "003",
        "원피스" : "020",
        "신발" : "005",
        "가방" : "004",
        "모자" : "007",
        "액세서리" : "011",
        "뷰티" : "015",
        "라이프": "012" 
        }
        date_db = {
            "1일" : "1d",
            "1주일" : "1w",
            "1개월" : "1m",
            "3개월" : "3m",
            "1년" : "1y"
        }
        while True:
            try:
                limit = int(input("수집할 데이터의 수를 입력하세요: "))
                break
            except ValueError:
                print("올바른 숫자를 입력하세요")
        while True:
            while True:
                keyword = input("상의, 바지, 아우터, 원피스, 신발, 가방, 모자, 액세서리, 뷰티, 라이프 중 한 가지 키워드를 입력하세요: ")
                if keyword in category:
                    break
                else:
                    print("키워드가 올바르지 않습니다. 다시 입력해주세요.")
            while True:
                date = input("1일, 1주일, 1개월, 3개월, 1년 중 수집 기간을 선택하세요: ")
                if date in date_db:
                    break
                else:
                    print("수집기간이 올바르지 않습니다. 다시 입력해주세요.")
                    
            url = f"https://www.musinsa.com/categories/item/{category[keyword]}?device=mw&sortCode={date_db[date]}"
            print("데이터 수집중.....")
            break
                
        #카테고리에 맞는 url로 이동
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'category__sc-')]")))
        
        #로딩 대기
        search_era = driver.find_element(By.XPATH, "//div[contains(@class, 'category__sc-')]")
        if search_era != driver.find_element(By.XPATH, "//div[contains(@class, 'category__sc-')]"):
            raise ValueError("search_era not found")
        
        #크롤링
        clothes_db = page_crawling(driver,10000,limit)
        
        #저장
        with open(f"{keyword}_musinsa_top{limit}_{date}기준", "w", newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["판매처", "제품명", "할인 전 판매가", "할인율", "판매가", "재고 상태"])
            for clothes in clothes_db:
                writer.writerow(clothes.values())
        
        print("CSV파일이 성공적으로 저장되었습니다.")
    
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
    
    finally:
        print("크롤러 종료")
        driver.quit()

crawler()