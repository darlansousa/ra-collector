import os
import selenium
import sys
from selenium import webdriver
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from util.functions import login, wait


def show_version():
    site = os.environ.get('COLLECTOR_SITE')
    login_page = os.environ.get('COLLECTOR_LOGIN_PAGE')
    target_page = os.environ.get('COLLECTOR_TARGET_PAGE')
    print("Used version:", selenium.__version__)
    print("site: ", site)
    print("login: ", login_page)
    print("target: ", target_page)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if sys.argv[1] == "login":
        user = sys.argv[2]
        password = sys.argv[3]
        login(driver, user, password)
        print("Press exit to close...")
        key = input()
        if key == "exit":
            driver.close()
            exit(0)
        else:
            input()


if __name__ == '__main__':
    show_version()
