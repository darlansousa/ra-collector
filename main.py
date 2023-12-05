import validators
import selenium
from selenium import webdriver
from selenium.webdriver.ie.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
from tkinter import simpledialog

from db.functions import *
from util.functions import *


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--disable-user-media-security=true")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


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
    messagebox.showinfo("Informações", f"Selenium version: {selenium.__version__}")


def collect_urls(conn, driver, total_items):
    options = messagebox.askquestion("Aguardando login...", "O login foi concluído?")
    if options != 'yes':
        return
    driver.get(os.environ.get('COLLECTOR_TARGET_PAGE'))
    accept_cookies(driver)
    get_all_urls(conn, driver, total_items)


def collect_data_from_url(conn, driver):
    url = simpledialog.askstring(title="Coleta por url", prompt="Digite a url da reclamação")
    if url:
        if not validators.url(url):
            messagebox.showerror("Validação", "Url inválida!")
            return
        complaint = get_complaint_infos(driver, url)
        if complaint:
            if register_complaint(conn, complaint):
                done_complaint_process(conn, complaint.cod)
                messagebox.showinfo("Informação", "Reclamação coletada")
        else:
            messagebox.showerror("Erro", "Reclamação não registrada")


def do_all(conn, driver, total_items):
    driver.get(os.environ.get('COLLECTOR_LOGIN_PAGE'))
    option = messagebox.askquestion("Aguardando login...", "O login foi concluído?")

    if option == 'yes':
        driver.minimize_window()
        driver.get(os.environ.get('COLLECTOR_TARGET_PAGE'))
        wait(5)
        accept_cookies(driver)
        wait(5)
        try:
            get_all_urls(conn, driver, total_items)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    option = messagebox.askquestion("Processar reclamações",
                                    "Deseja seguir com o processamento das reclamações?")
    if option == 'yes':
        process_urls(driver, conn)


if __name__ == '__main__':
    conn = get_connection()
    driver = None
    option = messagebox.askquestion("Abrir driver",
                                    "Deseja abrir o navegador?")
    if option == 'yes':
        driver = get_driver()
        driver.get(os.environ.get('COLLECTOR_TARGET_PAGE'))
        driver.set_permissions('clipboard-read', 'granted')
        driver.set_permissions('clipboard-write', 'granted')

    total_complaints = get_website_total_complaints()

    pending = get_pending_urls(conn)
    processed = get_processed(conn)

    window = ThemedTk(theme="arc")
    window.title("Assistente coletor de reclamações")
    window.geometry('400x800')
    window.configure(bg="#026BA3")
    window.grid_columnconfigure(0, weight=1, minsize=100)
    style = ttk.Style()

    style.configure('TButton', font=('Arial', 13), borderwidth='4')

    texts = [f"{total_complaints} reclamações no site",
             f"{len(pending)} reclamações pendentes",
             f"Reclamações processadas pelo coletor: {len(processed)}"]
    index = 0
    for text in texts:
        ttk.Label(window, text=text,
                  foreground="#FFFFFF",
                  padding=5,
                  font=('Arial', 13),
                  anchor="center",
                  background="#026BA3").grid(column=0, row=index)
        index = index + 1

    text = "Todas as reclamações foram registradas"
    if len(pending) > 0:
        text = f"{len(pending)} estão pendentes"

    steps = [('Executar todos os passos', lambda: do_all(conn, driver, total_complaints)),
             ('Aceitar cookies', lambda: accept_cookies(driver)),
             ('Coletar urls', lambda: collect_urls(conn, driver, total_complaints)),
             ('Coletar dados todas as urls', lambda: process_urls(driver, conn)),
             ('Coletar dados de uma url', lambda: collect_data_from_url(conn, driver)),
             ('Informações', show_info),
             ('Fechar', lambda: logout(driver))]
    index = 4
    for step in steps:
        ttk.Button(window, text=step[0],
                   command=step[1],
                   padding=5,
                   width=30
                   ).grid(column=0, row=index, pady=10)
        index = index + 1

    window.mainloop()
