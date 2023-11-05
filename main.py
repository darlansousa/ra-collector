import os
import selenium
from selenium import webdriver
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from db.functions import get_connection, save_urls, save_url_process, get_pending_urls, register_complaint
from util.functions import wait, get_all_urls, get_complaint_infos


def text():
    print("OK")
    conn = get_connection()
    save_url_process(conn, "xxxxxx/xxx")


def process_urls(driver, conn):
    result = []
    pending_list = get_pending_urls(conn)
    for url in pending_list:
        complaint = get_complaint_infos(driver, url)
        if complaint:
            if register_complaint(conn, complaint):
                result.append(complaint)
        else:
            wait(50)
            driver.refresh()
            complaint = get_complaint_infos(driver, url)
            if register_complaint(conn, complaint):
                result.append(complaint)

    messagebox.showinfo("Result", f"{len(result)} complaints processed")


def open_driver():
    conn = get_connection()
    option = webdriver.ChromeOptions()
    option.add_argument("start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    driver.get(os.environ.get('COLLECTOR_LOGIN_PAGE'))
    option = messagebox.askquestion("Waiting login.... ",
                                    "When you complete the login, click YES")
    if option == 'yes':
        driver.get(os.environ.get('COLLECTOR_TARGET_PAGE'))
        wait(5)
        try:
            urls = get_all_urls(driver)
            if len(urls) > 0:
                save_urls(conn, urls)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    option = messagebox.askquestion("Second Step ",
                                    "Do you want to process complaints?")
    if option == 'yes':
        process_urls(driver, conn)

    option = messagebox.askquestion("Waiting close.... ",
                                    "When you want to close, click YES")
    if option == 'yes':
        driver.close()


def show_info():
    collector_site = os.environ.get('COLLECTOR_SITE')
    access_page = os.environ.get('COLLECTOR_LOGIN_PAGE')
    target = os.environ.get('COLLECTOR_TARGET_PAGE')
    message = f"""
    Site: {collector_site}\n
    Login: {access_page}\n
    Collect Page: {target}
    """
    messagebox.showinfo(f"Selenium version: {selenium.__version__}", message)


if __name__ == '__main__':
    window = Tk()
    window.title("RA-Collector")
    window.geometry('500x300')
    window.attributes('-zoomed', True)
    frame = ttk.Frame(window, padding=20)
    frame.grid()
    site = os.environ.get('COLLECTOR_SITE')
    login_page = os.environ.get('COLLECTOR_LOGIN_PAGE')
    target_page = os.environ.get('COLLECTOR_TARGET_PAGE')
    ttk.Button(frame, text="Get complaints urls", command=open_driver).grid(column=0, row=8)
    ttk.Button(frame, text="Process pending complaints", command=text).grid(column=2, row=8)
    ttk.Button(frame, text="Infos", command=show_info).grid(column=3, row=8)
    ttk.Button(frame, text="Quit", command=window.destroy).grid(column=4, row=8)
    window.mainloop()
