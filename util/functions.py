import os
import random
import time

from model.Complainer import Complainer
from model.Complaint import Complaint

from selenium.webdriver.common.keys import Keys
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


def get_safe_single_element(fun, parameter):
    single_item = fun(parameter)
    if len(single_item) > 0:
        return single_item[0]
    return None

def get_safe_single_element_type(fun, type, parameter):
    single_item = fun(type, parameter)
    if len(single_item) > 0:
        return single_item[0]
    return None


def get_all_url_of_recs(driver):
    url_rec_n_resp = "https://www.reclameaqui.com.br/area-da-empresa/reclamacoes/nao-respondidas/"
    start = time.time()
    urls = []
    list_recs_id = "logged_area_complain_complain_card_list"
    list_recs_divs = get_safe_single_element_type(driver.find_elements_by_id, list_recs_id)
    if list_recs_divs:
        recs = list_recs_divs.find_elements_by_tag_name("section")
        elements_len = len(recs)
        for index in range(elements_len):
            recs[index].click()
            wait(3)
            url = driver.current_url
            urls.append(url)
            driver.refresh()
            driver.get(url_rec_n_resp)
            wait(5)
            list_recs_divs = get_safe_single_element_type(driver.find_elements_by_id, list_recs_id)
            recs = list_recs_divs.find_elements_by_tag_name("section")

    end = time.time()
    elapsed_time = end - start
    print('Execution time:', elapsed_time, 'seconds')
    return urls


def get_rec_infos(driver, url):
    driver.get(url)
    wait(5)
    rec = get_complainers(driver)
    if rec:
        print(rec.json())
    else:
        print("Error to get Rec")


def get_complainers(driver):
    start = time.time()
    info_container_class = "eDtPlq"
    sec_info_container_class = "fBIAOk"
    additional_info_class = "fczbZ"
    infos_class = "ljuKit"
    title_class = "dTQXop"
    name_class = "jrwOZz"
    rec_description_class = "ezeDJG"
    expand_button_name = "[data-testid='expand-btn']"
    info_container = get_safe_single_element_type(driver.find_elements_by_class_name, info_container_class)
    sec_info_container = get_safe_single_element_type(driver.find_elements_by_class_name, sec_info_container_class)
    additional_info_container = get_safe_single_element_type(driver.find_elements_by_class_name, additional_info_class)
    title_element = get_safe_single_element_type(driver.find_elements_by_class_name, title_class)
    name_element = get_safe_single_element_type(driver.find_elements_by_class_name, name_class)
    if info_container is None:
        return None
    infos = info_container.find_elements_by_class_name(infos_class)
    sec_infos = sec_info_container.find_elements_by_class_name(infos_class)

    expand_button = get_safe_single_element_type(additional_info_container.find_elements_by_css_selector, expand_button_name)
    if expand_button:
        expand_button.click()

    additional_infos = additional_info_container.find_elements_by_class_name(infos_class)
    description_container = get_safe_single_element_type(driver.find_elements_by_class_name, rec_description_class)

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


def login(driver, user, password):
    login_input_class = "sc-kpDqfm"
    password_input_class = "sc-cPiKLX"
    login_page = os.environ.get('COLLECTOR_LOGIN_PAGE')
    driver.get(login_page)
    wait(5)
    login_input = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, login_input_class)
    password_input = get_safe_single_element_type(driver.find_elements, By.CLASS_NAME, password_input_class)

    if login_input is not None and password_input is not None:
        login_input.send_keys(user + Keys.DOWN + Keys.RETURN)
        password_input.send_keys(password + Keys.DOWN + Keys.RETURN)
        return

    print("Error to login")
