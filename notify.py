from plyer import notification
import ctypes
import sys

url = sys.argv[1]

ctypes.windll.kernel32.FreeConsole()

ntf = notification.notify(
    title='CUIDADO!',
    message=f'A URL {url} foi encontrada na blacklist.',
    app_icon=r'C:\Users\User\Downloads\spy.ico',
    timeout=7  # Duração da notificação em segundos
    )
print(ntf)

