import time

try:
    import network
    import urequests
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

    TELEGRAM_DISPONIVEL = True
except Exception:
    TELEGRAM_DISPONIVEL = False


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

TELEGRAM_CHECK_MS = 5000

wifi_conectado = False
ultimo_check = 0
telegram_offset = 0

BOT_URL = ""

if TELEGRAM_DISPONIVEL:
    BOT_URL = "https://api.telegram.org/bot" + TELEGRAM_TOKEN


def esta_ativo():
    """Informa se o Telegram esta configurado e conectado."""
    return TELEGRAM_DISPONIVEL and wifi_conectado


def url_encode(texto):
    """Codifica texto em formato seguro para envio HTTP."""
    resultado = ""

    for byte in texto.encode("utf-8"):
        if (
            48 <= byte <= 57 or
            65 <= byte <= 90 or
            97 <= byte <= 122 or
            byte in (45, 46, 95)
        ):
            resultado += chr(byte)
        elif byte == 32:
            resultado += "+"
        else:
            resultado += "%{:02X}".format(byte)

    return resultado


def conectar_wifi():
    """Conecta o ESP32 ao Wi-Fi do Wokwi."""
    global wifi_conectado

    if not TELEGRAM_DISPONIVEL:
        print("Telegram desativado: config.py nao encontrado")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        inicio = time.ticks_ms()

        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), inicio) > 10000:
                print("Falha ao conectar no Wi-Fi")
                wifi_conectado = False
                return False

            time.sleep_ms(300)

    wifi_conectado = True
    print("Wi-Fi conectado:", wlan.ifconfig())
    return True


def enviar(mensagem):
    """Envia uma mensagem para o chat configurado no Telegram."""
    if not esta_ativo():
        return False

    url = BOT_URL + "/sendMessage"

    payload = "chat_id={}&text={}".format(
        TELEGRAM_CHAT_ID,
        url_encode(mensagem)
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        resposta = urequests.post(url, data=payload, headers=headers)
        sucesso = resposta.status_code == 200

        print("Telegram HTTP:", resposta.status_code)

        resposta.close()
        return sucesso

    except Exception as erro:
        print("Erro ao enviar Telegram:", erro)
        return False


def sincronizar_comandos_antigos():
    """Atualiza o offset para evitar executar comandos antigos ao iniciar."""
    global telegram_offset

    if not esta_ativo():
        return

    url = BOT_URL + "/getUpdates?timeout=0"

    try:
        resposta = urequests.get(url)
        texto = resposta.text
        resposta.close()

        posicao = 0
        maior_update = -1

        while True:
            update_pos = texto.find('"update_id":', posicao)

            if update_pos == -1:
                break

            inicio_id = update_pos + len('"update_id":')
            fim_id = texto.find(",", inicio_id)

            update_id = int(texto[inicio_id:fim_id].strip())

            if update_id > maior_update:
                maior_update = update_id

            posicao = fim_id

        if maior_update >= 0:
            telegram_offset = maior_update + 1
            print("Telegram offset sincronizado:", telegram_offset)

    except Exception as erro:
        print("Erro ao sincronizar comandos Telegram:", erro)


def iniciar():
    """Inicializa a comunicacao remota."""
    if conectar_wifi():
        sincronizar_comandos_antigos()
        return True

    return False


def buscar_comandos(agora):
    """Busca comandos recebidos no Telegram de forma periodica."""
    global ultimo_check, telegram_offset

    comandos = []

    if not esta_ativo():
        return comandos

    if time.ticks_diff(agora, ultimo_check) < TELEGRAM_CHECK_MS:
        return comandos

    ultimo_check = agora

    url = BOT_URL + "/getUpdates?timeout=0"

    if telegram_offset > 0:
        url += "&offset={}".format(telegram_offset)

    try:
        resposta = urequests.get(url)
        texto = resposta.text
        resposta.close()

        posicao = 0

        while True:
            update_pos = texto.find('"update_id":', posicao)

            if update_pos == -1:
                break

            inicio_id = update_pos + len('"update_id":')
            fim_id = texto.find(",", inicio_id)

            update_id = int(texto[inicio_id:fim_id].strip())
            telegram_offset = update_id + 1

            text_pos = texto.find('"text":"', fim_id)

            if text_pos != -1:
                inicio_texto = text_pos + len('"text":"')
                fim_texto = texto.find('"', inicio_texto)

                comando = texto[inicio_texto:fim_texto]
                comandos.append(comando)

            posicao = fim_id

    except Exception as erro:
        print("Erro ao buscar comandos Telegram:", erro)

    return comandos