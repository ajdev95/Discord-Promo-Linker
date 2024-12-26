import os
from datetime import datetime
from itertools import cycle
import requests
from colorama import Fore

TOKENS_FILE = "Input/tokens.txt"
PROXIES_FILE = "Input/proxies.txt"
PROMOS_FILE = "Input/promos.txt"
DATE_FOLDER = datetime.now().strftime('%m-%d-%Y %I-%M-%S %p')
OUTPUT_FOLDER = f"Output/{DATE_FOLDER}"

TOKENS_OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "tokens.txt")
PROMOS_OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "promos.txt")
COMBINED_OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "combined.txt")

def ensure_folder_exists(folder_path):
    os.makedirs(folder_path, exist_ok=True)

def load_lines(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

tokens = load_lines(TOKENS_FILE)
proxies = load_lines(PROXIES_FILE)
promos = load_lines(PROMOS_FILE)
proxy_pool = cycle(proxies)

def time_right_now():
    return datetime.now().strftime("%I:%M %p")

def write_to_file(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content + '\n')

def update_file(file_path, lines_to_keep):
    with open(file_path, 'w') as file:
        file.writelines(line + '\n' for line in lines_to_keep)

def process_tokens():
    ensure_folder_exists(OUTPUT_FOLDER)

    for token_line in tokens:
        try:
            parts = token_line.split(":")
            token = parts[-1] if len(parts) > 2 else parts[0]

            proxy = next(proxy_pool)
            proxies = {
                "http": f"http://{proxy}",
            }

            for full_promo in promos:
                try:
                    promo_id = full_promo.split('/')[5]
                    promo_jwt = full_promo.split('/')[6]

                    promo_url = f"https://discord.com/api/v9/entitlements/partner-promotions/{promo_id}"
                    headers = {
                        "authorization": token,
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'application/json',
                        'origin': 'https://discord.com',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    }

                    cookies = {
                        '__dcfduid': '96a01120bff511efb3d87b734df1cccf',
                        '__sdcfduid': '96a01121bff511efb3d87b734df1cccffa218a58b07acffb259a0fb994dc7ad9ed697b2b1352b21a8764a3ad7c2440f1',
                        '__cfruid': 'f7e97ed9efd61a2ea0d86ce92837eed92ee927e8-1734824705',
                        '_cfuvid': '5hwaobEzkTNfvOeFwzX_AEwtRD58I1VL7ooNPEHpJE4-1734824705202-0.0.1.1-604800000',
                        'cf_clearance': 'vlOq2lXbYXin0Q9xOI2R5KNbdbtSp1rulhz5_CQ.yYs-1734824705-1.2.1.1-MKA.LKFRt848vAZ9kfrZ7DbIqer3HlZ7x7tgm3ECv7UiUXcrc2YCy9racSLQBbNlI8qwwM7gHpToB2R66dwia2wGwgtXCt_ONkLUG1kpYJNZmJv1qSvtP_ENBrgK50Jmink78BTs8EYD.FKfP.JkvXkwENhfOhFoEYroAxCvrzFfDiNQbY5XJ4b.agJiSrCw7weceQ3Z3j.7_TfO2Vxk0UbeYuOtb.zl4.IiH2YYgzA9R.uXBHepIP9079GgwuixY.imnNhTFo.7os3V9r4TprAGIQG_ngs968Z7SGv9hEvebq6vVcq8gC8ZVeNmsLyeBICZXA66pDcwQswp5ryfWAJkNp2k0zvRdFmDLOvuEPcLe6goyuL_hd5hF73WmAMSA0qlGebXbILnkG9VXv34Og',
                    }

                    response = requests.post(
                        promo_url,
                        headers=headers,
                        json={"jwt": promo_jwt},
                        proxies=proxies,
                        cookies=cookies
                    )

                    if response.status_code == 200:
                        promo_data = response.json()
                        promo_redemption_id = promo_data.get("code")

                        if promo_redemption_id:
                            print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTCYAN_EX}PROMO{Fore.RESET}  | Retrieved promo code: {promo_redemption_id}")
                            write_to_file(PROMOS_OUTPUT_FILE, f"https://promo.discord.gg/{promo_redemption_id}")
                            write_to_file(TOKENS_OUTPUT_FILE, token_line)
                            write_to_file(COMBINED_OUTPUT_FILE, f"{token_line}|https://promo.discord.gg/{promo_redemption_id}")
                            
                            promos.remove(full_promo)
                            tokens.remove(token_line)
                            update_file(PROMOS_FILE, promos)
                            update_file(TOKENS_FILE, tokens)

                        else:
                            print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET}  | No promo code found.")
                            update_file(PROMOS_FILE, promos)
                            update_file(TOKENS_FILE, tokens)
                    else:
                        print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET}  | Failed request: {response.text}")
                        update_file(TOKENS_FILE, tokens)

                    break 

                except Exception as e:
                    print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET}  | Exception: {str(e)}")
                    break 

        except Exception as e:
            print(f"{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET}  | Exception: {str(e)}")
            break

if __name__ == "__main__":
    process_tokens()
    input(f"\n{Fore.LIGHTWHITE_EX}{time_right_now()} | {Fore.RESET}{Fore.LIGHTMAGENTA_EX}INFO{Fore.RESET}{Fore.LIGHTWHITE_EX}{Fore.LIGHTWHITE_EX}   | Press Enter To Exit: {Fore.RESET}")