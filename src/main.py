from machine import Pin, ADC
import time

print("Teste")
print("Iniciando firmware de monitoramento de luminosidade...")

# Telegram fica opcional:
# - Localmente, se existir config.py, o Telegram funciona.
# - No GitHub Actions, sem config.py, o firmware roda normalmente sem Telegram.
try:
    import network
    import urequests
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

    TELEGRAM_ATIVO = True
except Exception:
    TELEGRAM_ATIVO = False


# Definição dos pinos utilizados
LED_PIN = 2
BUTTON_PIN = 15
LDR_PIN = 34

# Modos de operação
AUTOMATICO = 0
MANUAL = 1

# Estados possíveis do sistema
OFF = 0
MONITORANDO = 1
ALERTA = 2
MANUAL_NORMAL = 3
MANUAL_ALERTA = 4

# Inicialização dos componentes
led = Pin(LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)

# Configurações de controle
DEBOUNCE_MS = 300
LONG_PRESS_MS = 1000
BLINK_ALERTA_MS = 200
TELEGRAM_CHECK_MS = 5000

# Limiares de histerese para o LDR
LIMIAR_ENTRA_ALERTA = 2500
LIMIAR_SAI_ALERTA = 1800

# Variáveis de controle do firmware
modo_operacao = AUTOMATICO
estado_sistema = OFF

ultimo_clique = 0
tempo_inicio_pressao = 0
estado_anterior_botao = 1

ultimo_blink = 0
estado_led_piscando = False

# Variáveis de Telegram
wifi_conectado = False
ultimo_check_telegram = 0
telegram_offset = 0

BOT_URL = ""
if TELEGRAM_ATIVO:
    BOT_URL = "https://api.telegram.org/bot" + TELEGRAM_TOKEN

# Registro simples dos eventos mais recentes
eventos = []
contador_alertas = 0


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

    if not TELEGRAM_ATIVO:
        print("Telegram desativado: config.py nao encontrado")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect("Wokwi-GUEST", "")

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


def enviar_telegram(mensagem):
    """Envia uma mensagem para o chat configurado no Telegram."""
    if not TELEGRAM_ATIVO or not wifi_conectado:
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
    """Evita executar comandos antigos ao iniciar o sistema."""
    global telegram_offset

    if not TELEGRAM_ATIVO or not wifi_conectado:
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


def registrar_evento(mensagem, notificar=False):
    """Registra evento localmente e, opcionalmente, envia ao Telegram."""
    global eventos

    print(mensagem)

    eventos.append(mensagem)

    if len(eventos) > 5:
        eventos.pop(0)

    if notificar:
        enviar_telegram(mensagem)


def obter_nome_modo():
    if modo_operacao == AUTOMATICO:
        return "AUTOMATICO"

    return "MANUAL"


def obter_nome_estado():
    if estado_sistema == OFF:
        return "OFF"

    if estado_sistema == MONITORANDO:
        return "MONITORANDO"

    if estado_sistema == ALERTA:
        return "ALERTA"

    if estado_sistema == MANUAL_NORMAL:
        return "MANUAL_NORMAL"

    if estado_sistema == MANUAL_ALERTA:
        return "MANUAL_ALERTA"

    return "DESCONHECIDO"


def montar_status():
    luminosidade = ler_sensor_luminosidade()

    return (
        "Status do Sistema\n"
        "Modo: {}\n"
        "Estado: {}\n"
        "Luminosidade: {}\n"
        "Alertas registrados: {}\n"
        "Ultimo evento: {}"
    ).format(
        obter_nome_modo(),
        obter_nome_estado(),
        luminosidade,
        contador_alertas,
        eventos[-1] if eventos else "Nenhum evento registrado"
    )


def montar_eventos():
    if not eventos:
        return "Nenhum evento registrado."

    texto = "Ultimos eventos:\n"

    for indice, evento in enumerate(eventos):
        texto += "{}. {}\n".format(indice + 1, evento)

    return texto


def montar_help():
    return (
        "Comandos disponiveis:\n"
        "/ligar - liga o sistema\n"
        "/desligar - desliga o sistema\n"
        "/status - mostra estado atual\n"
        "/auto - ativa modo automatico\n"
        "/manual - ativa modo manual\n"
        "/forcar_alerta - forca alerta manual\n"
        "/normal - forca sinal normal manual\n"
        "/eventos - lista ultimos eventos\n"
        "/help - mostra esta ajuda"
    )


def processar_comando_telegram(comando):
    """Executa comandos recebidos remotamente pelo Telegram."""
    global modo_operacao, estado_sistema

    comando = comando.strip().lower()

    if comando == "/ligar":
        if modo_operacao == AUTOMATICO:
            estado_sistema = MONITORANDO
            registrar_evento("Comando remoto: sistema ligado em AUTOMATICO", True)
        else:
            estado_sistema = MANUAL_NORMAL
            registrar_evento("Comando remoto: sistema ligado em MANUAL", True)

    elif comando == "/desligar":
        estado_sistema = OFF
        registrar_evento("Comando remoto: sistema desligado", True)

    elif comando == "/status":
        enviar_telegram(montar_status())

    elif comando == "/auto":
        modo_operacao = AUTOMATICO
        estado_sistema = MONITORANDO
        registrar_evento("Comando remoto: modo AUTOMATICO ativado", True)

    elif comando == "/manual":
        modo_operacao = MANUAL
        estado_sistema = MANUAL_NORMAL
        registrar_evento("Comando remoto: modo MANUAL ativado", True)

    elif comando == "/forcar_alerta":
        modo_operacao = MANUAL
        estado_sistema = MANUAL_ALERTA
        registrar_evento("Comando remoto: alerta manual forcado", True)

    elif comando == "/normal":
        modo_operacao = MANUAL
        estado_sistema = MANUAL_NORMAL
        registrar_evento("Comando remoto: sinal normal forcado", True)

    elif comando == "/eventos":
        enviar_telegram(montar_eventos())

    elif comando == "/help":
        enviar_telegram(montar_help())

    else:
        enviar_telegram("Comando nao reconhecido. Use /help.")


def verificar_comandos_telegram(agora):
    """Consulta periodicamente comandos enviados ao bot."""
    global ultimo_check_telegram, telegram_offset

    if not TELEGRAM_ATIVO or not wifi_conectado:
        return

    if time.ticks_diff(agora, ultimo_check_telegram) < TELEGRAM_CHECK_MS:
        return

    ultimo_check_telegram = agora

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

                print("Comando Telegram recebido:", comando)
                processar_comando_telegram(comando)

            posicao = fim_id

    except Exception as erro:
        print("Erro ao verificar comandos Telegram:", erro)


def ler_sensor_luminosidade():
    """Realiza a leitura analógica do sensor LDR."""
    return ldr.read()


def tratar_botao(agora):
    """Identifica clique curto e clique longo do botão."""
    global tempo_inicio_pressao, estado_anterior_botao, ultimo_clique

    leitura_atual = button.value()

    if leitura_atual == 0 and estado_anterior_botao == 1:
        tempo_inicio_pressao = agora

    if leitura_atual == 1 and estado_anterior_botao == 0:
        duracao_pressao = time.ticks_diff(agora, tempo_inicio_pressao)

        if time.ticks_diff(agora, ultimo_clique) > DEBOUNCE_MS:
            ultimo_clique = agora

            if duracao_pressao >= LONG_PRESS_MS:
                alternar_modo_operacao()
            else:
                processar_clique_curto()

    estado_anterior_botao = leitura_atual


def processar_clique_curto():
    """Processa ações de clique curto conforme o modo atual."""
    global estado_sistema

    if modo_operacao == AUTOMATICO:
        if estado_sistema == OFF:
            estado_sistema = MONITORANDO
            registrar_evento("Sistema ligado: MODO AUTOMATICO / MONITORANDO", True)
        else:
            estado_sistema = OFF
            registrar_evento("Sistema desligado: OFF", True)

    elif modo_operacao == MANUAL:
        if estado_sistema == MANUAL_NORMAL:
            estado_sistema = MANUAL_ALERTA
            registrar_evento("Modo MANUAL: alerta forcado", True)
        else:
            estado_sistema = MANUAL_NORMAL
            registrar_evento("Modo MANUAL: sinal normal forcado", True)


def alternar_modo_operacao():
    """Alterna entre os modos AUTOMATICO e MANUAL."""
    global modo_operacao, estado_sistema

    if modo_operacao == AUTOMATICO:
        modo_operacao = MANUAL
        estado_sistema = MANUAL_NORMAL
        registrar_evento("Modo alterado: MANUAL", True)
        registrar_evento("Controle manual ativo: sinal normal forcado", False)

    else:
        modo_operacao = AUTOMATICO
        estado_sistema = MONITORANDO
        registrar_evento("Modo alterado: AUTOMATICO", True)
        registrar_evento("Sensor LDR voltou a controlar o sistema", False)


def atualizar_estado_automatico(valor_luz):
    """Atualiza os estados automáticos conforme a luminosidade."""
    global estado_sistema, contador_alertas

    if estado_sistema == MONITORANDO:
        if valor_luz > LIMIAR_ENTRA_ALERTA:
            estado_sistema = ALERTA
            contador_alertas += 1
            registrar_evento("ALERTA: baixa luminosidade detectada", True)

    elif estado_sistema == ALERTA:
        if valor_luz < LIMIAR_SAI_ALERTA:
            estado_sistema = MONITORANDO
            registrar_evento("Luminosidade restabelecida: MONITORANDO", True)


def piscar_led(agora, intervalo):
    """Controla a piscagem não bloqueante do LED."""
    global ultimo_blink, estado_led_piscando

    if time.ticks_diff(agora, ultimo_blink) >= intervalo:
        ultimo_blink = agora
        estado_led_piscando = not estado_led_piscando
        led.value(estado_led_piscando)


def atualizar_sinalizacao_led(agora):
    """Atualiza a sinalização visual conforme o estado do sistema."""
    if estado_sistema == OFF:
        led.value(0)

    elif estado_sistema == MONITORANDO:
        led.value(1)

    elif estado_sistema == ALERTA:
        piscar_led(agora, BLINK_ALERTA_MS)

    elif estado_sistema == MANUAL_NORMAL:
        led.value(1)

    elif estado_sistema == MANUAL_ALERTA:
        piscar_led(agora, BLINK_ALERTA_MS)


# Inicialização da conectividade
if TELEGRAM_ATIVO:
    if conectar_wifi():
        sincronizar_comandos_antigos()
        registrar_evento("Sistema IoT iniciado com Telegram ativo", True)
    else:
        registrar_evento("Sistema iniciado sem conexao Telegram")
else:
    registrar_evento("Sistema iniciado sem Telegram")

# Loop principal
while True:
    instante_atual = time.ticks_ms()
    luminosidade_atual = ler_sensor_luminosidade()

    tratar_botao(instante_atual)

    if modo_operacao == AUTOMATICO and estado_sistema != OFF:
        atualizar_estado_automatico(luminosidade_atual)

    verificar_comandos_telegram(instante_atual)
    atualizar_sinalizacao_led(instante_atual)