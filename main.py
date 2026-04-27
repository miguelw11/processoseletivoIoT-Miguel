from machine import Pin, ADC
import time

# =========================
# PINOS
# =========================
LED_PIN = 2
BUTTON_PIN = 15
LDR_PIN = 34

# =========================
# MODOS
# =========================
AUTOMATICO = 0
MANUAL = 1

# =========================
# ESTADOS
# =========================
OFF = 0
MONITORANDO = 1
ALERTA = 2
MANUAL_NORMAL = 3
MANUAL_ALERTA = 4

# =========================
# HARDWARE
# =========================
led = Pin(LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)

# =========================
# CONFIGURAÇÕES
# =========================
DEBOUNCE_MS = 300
LONG_PRESS_MS = 1000
BLINK_ALERTA_MS = 200

LIMIAR_ENTRA_ALERTA = 2500
LIMIAR_SAI_ALERTA = 1800

# =========================
# VARIÁVEIS
# =========================
modo = AUTOMATICO
estado = OFF

ultimo_clique = 0
tempo_botao_pressionado = 0
botao_anterior = 1

ultimo_blink = 0
led_piscando = False


def ler_sensor():
    return ldr.read()


def tratar_botao(agora):
    global tempo_botao_pressionado, botao_anterior, ultimo_clique

    leitura_atual = button.value()

    # botão acabou de ser pressionado
    if leitura_atual == 0 and botao_anterior == 1:
        tempo_botao_pressionado = agora

    # botão acabou de ser solto
    if leitura_atual == 1 and botao_anterior == 0:
        duracao = time.ticks_diff(agora, tempo_botao_pressionado)

        if time.ticks_diff(agora, ultimo_clique) > DEBOUNCE_MS:
            ultimo_clique = agora

            if duracao >= LONG_PRESS_MS:
                alternar_modo()
            else:
                clique_curto()

    botao_anterior = leitura_atual


def clique_curto():
    global estado

    if modo == AUTOMATICO:
        if estado == OFF:
            estado = MONITORANDO
            print("Sistema ligado: MODO AUTOMATICO / MONITORANDO")
        else:
            estado = OFF
            print("Sistema desligado: OFF")

    elif modo == MANUAL:
        if estado == MANUAL_NORMAL:
            estado = MANUAL_ALERTA
            print("Modo MANUAL: alerta forçado")
        else:
            estado = MANUAL_NORMAL
            print("Modo MANUAL: sinal normal forçado")


def alternar_modo():
    global modo, estado

    if modo == AUTOMATICO:
        modo = MANUAL
        estado = MANUAL_NORMAL
        print("Modo alterado: MANUAL")
        print("Controle manual ativo: sinal normal forçado")

    else:
        modo = AUTOMATICO
        estado = MONITORANDO
        print("Modo alterado: AUTOMATICO")
        print("Sensor LDR voltou a controlar o sistema")


def atualizar_estado_automatico(valor_luz):
    global estado

    if estado == MONITORANDO:
        if valor_luz > LIMIAR_ENTRA_ALERTA:
            estado = ALERTA
            print("ALERTA: baixa luminosidade detectada")

    elif estado == ALERTA:
        if valor_luz < LIMIAR_SAI_ALERTA:
            estado = MONITORANDO
            print("Luminosidade restabelecida: MONITORANDO")


def piscar_led(agora, intervalo):
    global ultimo_blink, led_piscando

    if time.ticks_diff(agora, ultimo_blink) >= intervalo:
        ultimo_blink = agora
        led_piscando = not led_piscando
        led.value(led_piscando)


def atualizar_led(agora):
    if estado == OFF:
        led.value(0)

    elif estado == MONITORANDO:
        led.value(1)

    elif estado == ALERTA:
        piscar_led(agora, BLINK_ALERTA_MS)

    elif estado == MANUAL_NORMAL:
        led.value(1)

    elif estado == MANUAL_ALERTA:
        piscar_led(agora, BLINK_ALERTA_MS)


while True:
    agora = time.ticks_ms()
    valor_luz = ler_sensor()

    tratar_botao(agora)

    if modo == AUTOMATICO and estado != OFF:
        atualizar_estado_automatico(valor_luz)

    atualizar_led(agora)