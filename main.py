import asyncio
import concurrent.futures
import csv
import cv2 as cv
import pyautogui
import pytesseract as tc
import re
import subprocess
import os
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "notify.py")
blacklist_path = os.path.join(current_dir, "blacklist.csv")
tesseract_dir = os.path.join(current_dir, "Tesseract")


def load_blacklist():
    blacklist = []
    with open(blacklist_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            blacklist.append(row[0])  # Assume que a URL está na primeira coluna do CSV
    return blacklist


def check_blacklist(url, blacklist):
    for item in blacklist:
        if item in url:
            return True
    return False


async def capture_and_process():
    screenshot = pyautogui.screenshot()
    temp_dir = tempfile.gettempdir()
    file_name = "Image.png"
    file_path = os.path.join(temp_dir, file_name)

    screenshot.save(file_path)

    imagem = cv.imread(file_path)
    gray = cv.cvtColor(imagem, cv.COLOR_BGR2GRAY)

    ret, threshold = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    way = tesseract_dir
    tc.pytesseract.tesseract_cmd = os.path.join(way, "tesseract.exe")
    txt = tc.image_to_string(imagem)

    padroes_url = ['http', 'https', 'hitps', 'hitp', 'ca', '', '', 'www.']
    urls_encontradas = set()

    for padrao in padroes_url:
        regex = re.escape(padrao) + r"(\S+)"
        matches = re.findall(regex, txt)

        if padrao == '':
            continue

        urls_encontradas.update(matches)

    return urls_encontradas


def process_urls(urls):
    urls_na_blacklist = []
    blacklist = load_blacklist()

    for url in urls:
        if check_blacklist(url, blacklist):
            urls_na_blacklist.append(url)

    return urls_na_blacklist


async def main():
    while True:
        if True:
            await asyncio.sleep(3)

            capture_task = asyncio.create_task(capture_and_process())

            urls_encontradas = await capture_task

            url_chunks = [list(urls_encontradas)[i:i+2] for i in range(0, len(urls_encontradas), 2)]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = await asyncio.gather(*(loop.run_in_executor(executor, process_urls, urls) for urls in url_chunks))

            urls_na_blacklist = [url for sublist in results for url in sublist]

            for url in urls_na_blacklist:
                print("URL encontrada na blacklist: {}".format(url))
                subprocess.Popen(["start", "", "/B", file_path, url], shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        else:
            print('O Google Chrome não está aberto.')

        await asyncio.sleep(7)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
