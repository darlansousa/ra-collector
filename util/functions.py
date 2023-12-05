import os
import math
import requests
import random
import time

from db.functions import save_urls
from model.Complainer import Complainer
from model.Complaint import Complaint
from tkinter import Tk

from selenium.webdriver.common.by import By


def get_safety_string_from_index(elements, index, default_value):
    try:
        return elements[index].text
    except IndexError:
        return default_value


def get_safety_from_index(elements, index):
    try:
        return elements[index]
    except IndexError:
        return None


def wait(seconds=None):
    if not seconds:
        seconds = random.randrange(2, 8)
    time.sleep(seconds)


def get_safe_single_element_type(fun, by_type, parameter):
    single_item = fun(by_type, parameter)
    if len(single_item) > 0:
        return single_item[0]
    return None


def accept_cookies(driver):
    wait(3)
    button = get_safe_single_element_type(driver.find_elements, By.CSS_SELECTOR, "[aria-label='allow cookies']")
    if button:
        driver.execute_script("arguments[0].click();", button)


def logout(driver):
    wait(3)
    button = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, "eiLCzj")
    if button:
        driver.execute_script("arguments[0].click();", button)
        wait(5)

    driver.close()


def get_all_urls(conn, driver, total_items):
    wait(5)
    items_per_page = 10
    num_pages = math.ceil(int(total_items) / items_per_page)
    for i in range(1, num_pages + 1):
        name = "[aria-label='botão da página {}']".format(i)
        item_ref = get_safe_single_element_type(driver.find_elements, By.CSS_SELECTOR, name)
        if item_ref:
            driver.execute_script("arguments[0].click();", item_ref)
            wait(5)
            get_all_urls_of_page(conn, driver)


def get_all_urls_of_page(conn, driver):
    start = time.time()
    list_recs_id = "logged_area_complain_complain_card_list"
    list_recs_divs = get_safe_single_element_type(driver.find_elements, By.ID, list_recs_id)
    if list_recs_divs:
        recs = list_recs_divs.find_elements(By.TAG_NAME, "section")
        elements_len = len(recs)
        for index in range(elements_len):
            save_urls(conn, get_cods(recs[index], driver))
            list_recs_divs = get_safe_single_element_type(driver.find_elements, By.ID, list_recs_id)
            if list_recs_divs:
                recs = list_recs_divs.find_elements(By.TAG_NAME, "section")
            else:
                wait(5)
                list_recs_divs = get_safe_single_element_type(driver.find_elements, By.ID, list_recs_id)
                recs = list_recs_divs.find_elements(By.TAG_NAME, "section")

    end = time.time()
    elapsed_time = end - start
    print('Execution time:', elapsed_time, 'seconds')


def get_cods(rec_element, driver):
    win = Tk()
    codes = []
    options = get_safe_single_element_type(rec_element.find_elements, By.CLASS_NAME, 'iTWEtF')
    if options:
        buttons = options.find_elements(By.TAG_NAME, 'button')
        copy_button = get_safety_from_index(buttons, 2)
        if copy_button:
            driver.execute_script("arguments[0].click();", copy_button)
            url = win.clipboard_get()
            if url:
                cod = url[-16:]
                codes.append(cod)

    win.destroy()
    return codes


def get_complaint_infos(driver, url):
    driver.get(url)
    wait(5)
    rec = get_complaints(driver)
    if rec:
        return rec

    return None


def get_complaints(driver):
    start = time.time()
    info_container_class = "eDtPlq"
    sec_info_container_class = "fBIAOk"
    additional_info_class = "fczbZ"
    infos_class = "ljuKit"
    title_class = "dTQXop"
    name_class = "jrwOZz"
    rec_description_class = "jTxpkE"
    expand_button_name = "[data-testid='expand-btn']"
    info_container = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, info_container_class)
    sec_info_container = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, sec_info_container_class)
    additional_info_container = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, additional_info_class)
    title_element = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, title_class)
    name_element = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, name_class)
    if info_container is None:
        return None
    accept_cookies(driver)
    infos = info_container.find_elements(By.CLASS_NAME, infos_class)
    sec_infos = sec_info_container.find_elements(By.CLASS_NAME, infos_class)

    expand_button = get_safe_single_element_type(additional_info_container.find_elements,
                                                 By.CSS_SELECTOR,
                                                 expand_button_name)
    if expand_button:
        driver.execute_script("arguments[0].click();", expand_button)

    additional_infos = additional_info_container.find_elements(By.CLASS_NAME, infos_class)
    description_container = get_safe_single_element_type(driver.find_elements,
                                                         By.CLASS_NAME,
                                                         rec_description_class)

    rec_title = title_element.text
    rec_name = name_element.text
    rec_cod = get_safety_string_from_index(infos, 0, "")
    rec_id = get_safety_string_from_index(infos, 1, "")
    rec_city = get_safety_string_from_index(infos, 2, "")
    rec_date_time = get_safety_string_from_index(infos, 3, "")
    rec_phone = get_safety_string_from_index(infos, 4, "")

    rec_cpf = get_safety_string_from_index(sec_infos, 0, "")
    rec_email = get_safety_string_from_index(sec_infos, 1, "")
    rec_phone2 = get_safety_string_from_index(sec_infos, 2, "")
    rec_phone3 = get_safety_string_from_index(sec_infos, 3, "")
    rec_is_client = get_safety_string_from_index(additional_infos, 0, "")
    rec_uc = get_safety_string_from_index(additional_infos, 1, "")
    rec_chanel = get_safety_string_from_index(additional_infos, 2, "")
    rec_reason = get_safety_string_from_index(additional_infos, 3, "")
    if description_container is None:
        return None

    rec_description = description_container.text

    client = Complainer(rec_cpf,
                        rec_name,
                        rec_city,
                        rec_email,
                        rec_phone,
                        rec_phone2,
                        rec_phone3,
                        rec_is_client,
                        rec_uc)

    reclamation = Complaint(rec_cod,
                            rec_id,
                            rec_title,
                            rec_date_time,
                            rec_chanel,
                            rec_reason,
                            rec_description,
                            client)

    end = time.time()
    elapsed_time = end - start
    print('Execution time:', elapsed_time, 'seconds')
    return reclamation


def get_website_total_complaints():
    url = os.environ.get('COLLECTOR_SITE_INFO_URL')
    payload = {}
    headers = {
        'Cookie': os.environ.get('COLLECTOR_SITE_INFO_COOKIE'),
        'User-Agent': os.environ.get('COLLECTOR_SITE_INFO_AGENT')
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    return response_json['complainResult']['complains']['count']
