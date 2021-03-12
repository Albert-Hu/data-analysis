# coding: utf8
from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

import argparse, time
import pandas as pd

def run(stock_code):
  opts = Options()
  opts.set_headless(headless=True)
  url = "https://mops.twse.com.tw/mops/web/t05st09_2"
  #This example requires Selenium WebDriver 3.13 or newer
  with webdriver.Chrome(options=opts, executable_path="./drivers/geckodriver") as driver:
    driver.get(url)
    Select(driver.find_element(By.ID, "isnew")).select_by_value("false")
    driver.find_element(By.ID, "co_id").send_keys(stock_code + Keys.RETURN)
    driver.find_element(By.ID, "date1").send_keys("100" + Keys.RETURN)
    driver.find_element(By.ID, "date2").send_keys("110" + Keys.RETURN)
    driver.find_element(By.CSS_SELECTOR, "input[type='button'][value=' 查詢 ']").click()
    time.sleep(1)
    html = BeautifulSoup(driver.page_source, "html.parser")
    for row in html.find_all('tr', attrs={"class": "odd"}):
      columns = row.find_all('td')
      columns = columns[4:5] + columns[6:18]
      columns = list(map(lambda c: ''.join(c.get_text().split()), columns))
      print(columns)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("code", type=str, help="The stock code.")
  args = parser.parse_args()
  run(args.code)
