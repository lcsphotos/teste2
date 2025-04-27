import threading
import time
import random
import os

# Morte ceifadora ASCII Art
reaper_art = r"""
                 .-.
                {{@}}
                 8@8
                88888
               8 888 8
              8  8  8 8
             8   8  8   8
            8    8  8    8
           8     8  8     8
          8      8  8      8
         8       8  8       8
         8       8  8       8
          8      8  8      8
           8     8  8     8
            8    8  8    8
             8   8  8   8
              8  8  8 8
               8 888 8
                88888
                 8@8
                 {{@}}
                  '-'
      🧹 DoS -  Lucas Navarro 🧹
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

def udp_flood():
    print("🚀 Iniciando UDP Flood... (ainda vamos montar essa função!)")
    # Aqui vamos construir depois!

def dns_amplification():
    print("🔊 Iniciando DNS Amplification... (ainda vamos montar!)")
    # Aqui vamos construir depois!

def http_amplification():
    print("🌐 Iniciando HTTP Amplification... (ainda vamos montar!)")
    # Aqui vamos construir depois!

def proxy_scraper():
    print("🕵️‍♂️ Scraping de proxies... (ainda vamos montar!)")
    # Aqui vamos construir depois!

def fake_botnet():
    print("🤖 Iniciando Botnet Fake... (ainda vamos montar!)")
    # Aqui vamos construir depois!

while True:
    opt = menu()

    if opt == "1":
        udp_flood()
    elif opt == "2":
        dns_amplification()
    elif opt == "3":
        http_amplification()
    elif opt == "4":
        proxy_scraper()
    elif opt == "5":
        fake_botnet()
    elif opt == "0":
        print("Encerrando o ataque... ☠️")
        break
    else:
        print("Opção inválida.")
    
    input("\nPressione Enter para voltar ao menu...")

