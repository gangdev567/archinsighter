from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import requests
import os
import time

# 웹드라이버 설정
print("웹드라이버 설정 중...")
driver_path = "C:/tools/projects/archinsighter/driver/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

def log(message):
    print(message)

def click_right_side_of_page():
    try:
        log("페이지의 오른쪽 부분을 클릭하기 위해 준비 중...")
        page_width = driver.execute_script("return document.body.scrollWidth")
        page_height = driver.execute_script("return document.body.scrollHeight")
        log(f"페이지 너비: {page_width}, 페이지 높이: {page_height}")

        right_side_x = page_width * 0.75  # 페이지 너비의 75% 지점
        right_side_y = page_height / 2
        log(f"클릭할 X 좌표: {right_side_x}, Y 좌표: {right_side_y}")

        # 페이지의 특정 위치로 스크롤
        driver.execute_script("window.scrollTo(arguments[0], arguments[1]);", right_side_x, right_side_y)

        # 스크롤된 위치에서 클릭
        actions = ActionChains(driver)
        actions.move_by_offset(right_side_x, right_side_y).click().perform()
        log("페이지의 오른쪽 부분 클릭 완료")

    except Exception as e:
        print(f"클릭 중 오류 발생: {e}")

def download_image(url, folder, index):
    """이미지를 다운로드하는 함수입니다."""
    print(f"이미지 {index} 다운로드 중: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{folder}/image_{index}.jpg", "wb") as file:
            file.write(response.content)
        print(f"이미지 {index} 저장 완료")
    else:
        print(f"이미지 {index} 다운로드 실패: HTTP {response.status_code}")

def download_gallery_images(project_id):
    """갤러리의 모든 이미지를 다운로드합니다."""
    print(f"프로젝트 {project_id}의 갤러리 페이지로 이동 중...")
    main_url = f"https://www.archdaily.com/{project_id}"
    driver.get(main_url)

    # 갤러리 페이지로 이동
    try:
        print("브라우저 창 최대화 중...")
        driver.maximize_window()  # 브라우저 창을 최대화합니다.

        print("갤러리 링크 찾는 중...")
        gallery_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gallery-thumbs-link"))).get_attribute("href")
        print(f"갤러리 링크 발견: {gallery_link}")
        driver.get(gallery_link)
    except TimeoutException:
        print("갤러리 링크를 찾을 수 없습니다. 페이지 로드 시간 초과.")
        driver.quit()
        return
    except NoSuchElementException:
        print("갤러리 링크를 찾을 수 없습니다.")
        driver.quit()
        return

    # 이미지를 저장할 폴더 생성
    folder = f"project_{project_id}_images"
    print(f"이미지를 저장할 폴더 생성 중: {folder}")
    os.makedirs(folder, exist_ok=True)

    index = 0
    last_img_url = ""

    while True:
        try:
            # 현재 페이지의 이미지 URL을 찾음
            print("현재 페이지의 이미지 URL 찾는 중...")
            img_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "figure img.js-gal-img.active-image")))
            img_url = img_element.get_attribute("data-largesrc")

            # 이미지 다운로드
            print(f"이미지 URL 발견: {img_url}")
            download_image(img_url, folder, index)
            index += 1

            # '다음' 버튼 클릭
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "next-image")))
            driver.execute_script("arguments[0].scrollIntoView(); window.scrollBy(0, -200);", next_button)
            next_button.click()

            # 페이지 로딩 대기
            time.sleep(5)  # 페이지가 완전히 로드될 때까지 5초 대기

        except TimeoutException as e:
            print(f"새 이미지 로드 시간 초과: {e}")
            break
        except NoSuchElementException as e:
            print(f"오류 발생 또는 마지막 이미지 도달: {e}")
            break
        except Exception as e:
            print(f"알 수 없는 오류 발생: {e}")
            break

    print(f"총 {index}개의 이미지를 다운로드했습니다.")
    driver.quit()

# 예시 프로젝트 ID
project_id = '1011616'
download_gallery_images(project_id)