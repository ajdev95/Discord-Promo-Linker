import os
from datetime import datetime
from itertools import cycle
import requests
from colorama import Fore
import json
import ctypes

inputTokens = "Input/tokens.txt"
inputProxies = "Input/proxies.txt"
inputPromos = "Input/promos.txt"

retrieved = 0
failed = 0
error = 0
threeMonths = 0
oneMonth = 0


def updateTitle():
    title = f"Retrieved: {retrieved} [3 Months: {threeMonths} | 1 Month: {oneMonth}] | Failed: {failed} | Error: {error}"
    ctypes.windll.kernel32.SetConsoleTitleW(title)

with open('config.json', 'r', encoding='utf-8-sig') as file:
    config_data = json.load(file)

if config_data['DatedOutput']:
    outputFolder = f"Output/{datetime.now().strftime('%m-%d-%Y %I-%M-%S %p')}"
else:
    outputFolder = "Output"

outputTokens = os.path.join(outputFolder, "tokens.txt")
outputPromos = os.path.join(outputFolder, "promos.txt")
outputCombined = os.path.join(outputFolder, "combined.txt")
outputusedPromos = os.path.join(outputFolder, "usedpromos.txt")


def folderExithm(folder_path):
    os.makedirs(folder_path, exist_ok=True)

def fileExithm(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

def clearOutput(folder_path):
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))

def loadLines(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return []

def writeFile(file_path, content):
    fileExithm(file_path)
    with open(file_path, 'a') as file:
        file.write(content + '\n')

def update_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(line + '\n' for line in lines)

def time_right_now():
    return datetime.now().strftime("%I:%M %p")

def processTokens():
    global retrieved, failed, error, oneMonth, threeMonths

    folderExithm(outputFolder)

    fileExithm(outputTokens)
    fileExithm(outputPromos)
    fileExithm(outputCombined)
    fileExithm(outputusedPromos)

    tokens = loadLines(inputTokens)
    proxies = loadLines(inputProxies) if config_data['UseProxies'] else []
    promos = loadLines(inputPromos)
    proxy_pool = cycle(proxies)

    for token_line in tokens[:]:
        token = token_line.split(":")[-1]
        proxy = {"http": f"http://{next(proxy_pool)}"} if proxies else None

        for full_promo in promos[:]:
            try:
                promo_id, promo_jwt = full_promo.split('/')[5:7]
                promo_url = f"https://discord.com/api/v9/entitlements/partner-promotions/{promo_id}"
                headers = {
                    "authorization": token,
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'content-type': 'application/json',
                    'origin': 'https://discord.com',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                }

                response = requests.post(promo_url, headers=headers, json={"jwt": promo_jwt}, proxies=proxy)

                if response.status_code == 200:
                    promo_data = response.json()
                    promo_redemption_id = promo_data.get("code")

                    if promo_redemption_id:
                        if promo_id == "1310745123109339258":
                            checkPromoType = f"{Fore.LIGHTGREEN_EX}3 Months{Fore.RESET}"
                            threeMonths += 1
                        elif promo_id == "1310745070936391821":
                            checkPromoType = f"{Fore.LIGHTYELLOW_EX}1 Month{Fore.RESET}"
                            oneMonth += 1
                        else:
                            checkPromoType = f"{Fore.LIGHTRED_EX}Unknown{Fore.RESET}"
                    
                        print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTCYAN_EX}PROMO{Fore.RESET} | Retrieved promo code {Fore.LIGHTWHITE_EX}[Code: {Fore.RESET}{Fore.LIGHTCYAN_EX}{promo_redemption_id}{Fore.RESET}{Fore.LIGHTWHITE_EX}{Fore.LIGHTWHITE_EX} | Duration: {Fore.RESET}{checkPromoType}{Fore.LIGHTWHITE_EX}]{Fore.RESET}")
                        writeFile(outputPromos, f"https://promos.discord.gg/{promo_redemption_id}")
                        writeFile(outputTokens, token_line)
                        writeFile(outputCombined, f"{token_line}|https://promos.discord.gg/{promo_redemption_id}")
                        writeFile(outputusedPromos, full_promo)

                        retrieved += 1
                        promos.remove(full_promo)
                        tokens.remove(token_line)

                        update_file(inputPromos, promos)
                        update_file(inputTokens, tokens)

                        updateTitle()
                        break
                else:
                    print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET} | Failed to retrieve promo {Fore.LIGHTWHITE_EX}[Error: {Fore.RESET}{Fore.LIGHTRED_EX}{response.text}{Fore.RESET}{Fore.LIGHTWHITE_EX}]{Fore.RESET}")
                    promos.remove(full_promo)
                    tokens.remove(token_line)
                    failed += 1
                    updateTitle()

                    update_file(inputPromos, promos)
                    update_file(inputTokens, tokens)

            except Exception as e:
                updateTitle()
                error += 1
                print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET} | Exception {Fore.LIGHTWHITE_EX}[Error: {Fore.RESET}{Fore.LIGHTRED_EX}{str(e)}{Fore.RESET}{Fore.LIGHTWHITE_EX}]{Fore.RESET}")


if __name__ == "__main__":
    folderExithm(outputFolder)
    updateTitle()

    os.system("cls" if os.name == "nt" else "clear")
    print(f"                                      {Fore.LIGHTMAGENTA_EX}Streamlab Promotion Linker {Fore.RESET}v1.5.0")
    print()

    if not config_data['DatedOutput']:
        user_input = input(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTYELLOW_EX}INFO{Fore.RESET}  | Clear output folder? ({Fore.LIGHTGREEN_EX}yes{Fore.RESET}/{Fore.LIGHTRED_EX}no{Fore.RESET}): {Fore.RESET}").strip().lower()

        if user_input in ["yes", "y"]:
            clearOutput(outputFolder)

        print()
        processTokens()
        input(f"\n{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTMAGENTA_EX}DONE{Fore.RESET}  | Press Enter to Exit: {Fore.RESET}")
