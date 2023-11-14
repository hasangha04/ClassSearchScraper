from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os

chromedriver_path = './chrome/chrome.exe' 

os.environ['PATH'] = f'{os.environ["PATH"]};{chromedriver_path}'

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://my.ec.seattleu.edu/Student/Student/Courses/Search')

# Parent element of the courses
parent_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'esg-col-sm-9'))
)

def click_checkbox(checkbox_id):
    checkbox_label = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'label[for="{checkbox_id}"]'))
    )
    
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_label)
    
    checkbox_label.click()
    
    WebDriverWait(driver, 2).until(EC.staleness_of(checkbox_label))

# Any filters that need to be applied
checkbox_selectors = [
    'STATICterm24SQ',
    'STATICacademicLevelUG',
]

for checkbox_selector in checkbox_selectors:
    click_checkbox(checkbox_selector)

def scrape_courses():
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '#course-resultul li'))
    )

    WebDriverWait(driver, 2)

    # Stores all of the courses on the current page
    list_items = driver.find_elements(By.CSS_SELECTOR, '#course-resultul li')

    for list_item in list_items:
        span_element = list_item.find_element(By.TAG_NAME, 'span')
        element_text = span_element.text

        requisites_div = list_item.find_element(By.XPATH, './/div[contains(@class, "search-coursedataheader") and contains(text(), "Requisites")]')
        requisites_info = requisites_div.find_element(By.XPATH, 'following-sibling::div/span').text.strip()

        if requisites_info == 'None':
            if "(5 Credits)" not in element_text and "(4 Credits)" not in element_text:
                output_string = f'Text: {element_text}\nRequisites: {requisites_info}\n---\n'

                print(output_string)

                # If you want to write to a file instead of printing to the console
                # with open('spring.txt', 'a') as file:
                #     file.write(output_string)

def go_to_next_page():
    next_page_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'course-results-next-page'))
    )
    driver.execute_script("arguments[0].click();", next_page_button)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'course-results-current-page'))
    )

# Get the total number of pages
total_pages_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'course-results-total-pages'))
)
total_pages = int(total_pages_element.text)

# Initial scraping of the first page
scrape_courses()

for _ in range(total_pages - 1):
    go_to_next_page()

    time.sleep(3)

    scrape_courses()

driver.quit()