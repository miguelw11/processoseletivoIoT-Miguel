from machine import Pin, ADC
import time

# =========================
# PINOS
# =========================
LED_PIN = 2
BUTTON_PIN = 15
LDR_PIN = 34

# =========================
# ESTADOS
# =========================
OFF = 0
MONITORANDO = 1
ALERTA = 2

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
BLINK_INTERVAL_MS = 200
LIMIAR_ENTRA_ALERTA = 2500
LIMIAR_SAI_ALERTA = 1800

# =========================
# VARIÁVEIS DE CONTROLE
# =========================
estado = OFF
ultimo_clique = 0
ultimo_blink = 0
led_piscando = False


def ler_sensor():
    return ldr.read()


def botao_foi_pressionado(agora):
    global ultimo_clique

    if button.value() == 0:
        if time.ticks_diff(agora, ultimo_clique) > DEBOUNCE_MS:
            ultimo_clique = agora
            return True

    return False


def alternar_sistema():
    global estado

    if estado == OFF:
        estado = MONITORANDO
        print("Sistema ligado: MONITORANDO")
    else:
        estado = OFF
        print("Sistema desligado: OFF")


def atualizar_estado(valor_luz):
    global estado

    if estado == MONITORANDO:
        if valor_luz > LIMIAR_ENTRA_ALERTA:
            estado = ALERTA
            print("ALERTA: baixa luminosidade detectada")

    elif estado == ALERTA:
        if valor_luz < LIMIAR_SAI_ALERTA:
            estado = MONITORANDO
            print("Luminosidade restabelecida: MONITORANDO")


def atualizar_led(agora):
    global ultimo_blink, led_piscando

    if estado == OFF:
        led.value(0)

    elif estado == MONITORANDO:
        led.value(1)

    elif estado == ALERTA:
        if time.ticks_diff(agora, ultimo_blink) >= BLINK_INTERVAL_MS:
            ultimo_blink = agora
            led_piscando = not led_piscando
            led.value(led_piscando)


while True:
    agora = time.ticks_ms()
    valor_luz = ler_sensor()

    if botao_foi_pressionado(agora):
        alternar_sistema()

    if estado != OFF:
        atualizar_estado(valor_luz)

    atualizar_led(agora)