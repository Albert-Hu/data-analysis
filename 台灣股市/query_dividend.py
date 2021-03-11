from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

import argparse

def run(stock_code):
  opts = Options()
  opts.set_headless(headless=True)

  #This example requires Selenium WebDriver 3.13 or newer
  with webdriver.Chrome(options=opts, executable_path='./drivers/geckodriver') as driver:
    wait = WebDriverWait(driver, 10)
    driver.get("https://google.com/ncr")
    driver.find_element(By.NAME, "q").send_keys("cheese" + Keys.RETURN)
    first_result = wait.until(presence_of_element_located((By.CSS_SELECTOR, "h3>div")))
    # print(first_result.get_attribute("textContent"))
    # print(driver.page_source)
    parser = BeautifulSoup(driver.page_source, 'html.parser')
    print(parser.title)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('code', help='The stock code.')
  args = parser.parse_args()
  run(args.code)
