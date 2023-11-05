import os
import selenium
from selenium import webdriver
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from db.functions import get_connection, save_urls, get_pending_urls, register_complaint, \
    done_complaint_process, get_processed
from util.functions import wait, get_all_urls, get_complaint_infos, accept_cookies, logout


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def step_1():
    conn = get_connection()
    driver = get_driver()
    driver.get(os.environ.get('COLLECTOR_LOGIN_PAGE'))
    option = messagebox.askquestion("Waiting login.... ",
                                    "When you complete the login, click YES")
    if option == 'yes':
        driver.get(os.environ.get('COLLECTOR_TARGET_PAGE'))
        wait(5)
        accept_cookies(driver)
        try:
            urls = get_all_urls(driver)
            if len(urls) > 0:
                save_urls(conn, urls)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    option = messagebox.askquestion("Second Step",
                                    "Do you want to process complaints?")
    if option == 'yes':
        process_urls(driver, conn)

    option = messagebox.askquestion("Waiting close.... ",
                                    "When you want to close, click YES")
    if option == 'yes':
        logout(driver)


def step_2():
    conn = get_connection()
    driver = get_driver()
    driver.get(os.environ.get('COLLECTOR_LOGIN_PAGE'))

    option = messagebox.askquestion("Waiting login.... ",
                                    "When you complete the login, click YES")
    if option == 'yes':
        process_urls(driver, conn)

    option = messagebox.askquestion("Waiting close.... ",
                                    "When you want to close, click YES")
    if option == 'yes':
        logout(driver)


def process_urls(driver, conn):
    result = []
    pending_list = get_pending_urls(conn)
    for url in pending_list:
        complaint = get_complaint_infos(driver, url)
        if complaint:
            if register_complaint(conn, complaint):
                done_complaint_process(conn, complaint.cod)
                result.append(complaint)
        else:
            wait(50)
            driver.refresh()
            complaint = get_complaint_infos(driver, url)
            if register_complaint(conn, complaint):
                done_complaint_process(conn, complaint.cod)
                result.append(complaint)

    messagebox.showinfo("Result", f"{len(result)} complaints processed")


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
    co = get_connection()
    pending = get_pending_urls(co)
    processed = get_processed(co)
    window = Tk()
    window.title("RA-Collector")
    window.geometry('500x300')
    window.attributes('-zoomed', True)
    frame = ttk.Frame(window, padding=20)
    frame.grid()
    site = os.environ.get('COLLECTOR_SITE')
    login_page = os.environ.get('COLLECTOR_LOGIN_PAGE')
    target_page = os.environ.get('COLLECTOR_TARGET_PAGE')
    ttk.Button(frame, text="Get complaints urls", command=step_1).grid(column=0, row=8)
    if len(pending) > 0:
        ttk.Button(frame, text=f"Process {len(pending)} pending complaints", command=step_2).grid(column=2, row=8)
    else:
        ttk.Label(text=f"All complaints processed").grid(column=0, row=10)
    ttk.Button(frame, text="Infos", command=show_info).grid(column=3, row=8)
    ttk.Button(frame, text="Quit", command=window.destroy).grid(column=5, row=8)
    ttk.Label(text=f"Processed complaints: {len(processed)}").grid(column=0, row=9)
    ttk.Label(text=f"Processed complaints: {len(processed)}").grid(column=0, row=9)
    window.mainloop()
