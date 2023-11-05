import os
import random
import time

from model.Complainer import Complainer
from model.Complaint import Complaint

from selenium.webdriver.common.by import By


def get_safety_string_from_index(elements, index, default_value):
    try:
        return elements[index].text
    except IndexError:
        return default_value


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
        button.click()


def logout(driver):
    wait(3)
    button = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, "eiLCzj")
    if button:
        button.click()
        wait(5)
        driver.close()



def get_all_urls(driver):
    all_recs = []
    list_pages = "sc-bWOGAC"
    list_pages_buttons = driver.find_element(By.CLASS_NAME, list_pages)
    items = list_pages_buttons.find_elements(By.TAG_NAME, "li")

    for index in range(len(items)):
        if items[index].text:
            name = "[aria-label='botão da página {}']".format(items[index].text)
            item_ref = get_safe_single_element_type(driver.find_elements, By.CSS_SELECTOR, name)
            item_ref.click()
            wait(5)
            rec_list_urls = get_all_urls_of_page(driver)
            all_recs.extend(rec_list_urls)
            list_pages_buttons = driver.find_element(By.CLASS_NAME, list_pages)
            items = list_pages_buttons.find_elements(By.TAG_NAME, "li")

    return all_recs


def get_all_urls_of_page(driver):
    url_rec_n_resp = os.environ.get('COLLECTOR_TARGET_PAGE')
    start = time.time()
    urls = []
    list_recs_id = "logged_area_complain_complain_card_list"
    list_recs_divs = get_safe_single_element_type(driver.find_elements, By.ID, list_recs_id)
    if list_recs_divs:
        recs = list_recs_divs.find_elements(By.TAG_NAME, "section")
        elements_len = len(recs)
        for index in range(elements_len):
            recs[index].click()
            wait(3)
            url = driver.current_url
            urls.append(url)
            driver.refresh()
            driver.get(url_rec_n_resp)
            wait(5)
            list_recs_divs = get_safe_single_element_type(driver.find_elements, By.ID, list_recs_id)
            recs = list_recs_divs.find_elements(By.TAG_NAME, "section")

    end = time.time()
    elapsed_time = end - start
    print('Execution time:', elapsed_time, 'seconds')
    return urls


def get_complaint_infos(driver, url):
    driver.get(url)
    wait(5)
    rec = get_complaints(driver)
    if rec:
        return rec
    else:
        return None


def get_complaints(driver):
    start = time.time()
    info_container_class = "eDtPlq"
    sec_info_container_class = "fBIAOk"
    additional_info_class = "fczbZ"
    infos_class = "ljuKit"
    title_class = "dTQXop"
    name_class = "jrwOZz"
    rec_description_class = "ezeDJG"
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
        expand_button.click()

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
