from machine import Pin, ADC
import time

# Print para validação do Actions
print("Teste")
print("Iniciando firmware de monitoramento de luminosidade...")

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
            print("Sistema ligado: MODO AUTOMATICO / MONITORANDO")
        else:
            estado_sistema = OFF
            print("Sistema desligado: OFF")

    elif modo_operacao == MANUAL:
        if estado_sistema == MANUAL_NORMAL:
            estado_sistema = MANUAL_ALERTA
            print("Modo MANUAL: alerta forçado")
        else:
            estado_sistema = MANUAL_NORMAL
            print("Modo MANUAL: sinal normal forçado")


def alternar_modo_operacao():
    """Alterna entre os modos AUTOMATICO e MANUAL."""
    global modo_operacao, estado_sistema

    if modo_operacao == AUTOMATICO:
        modo_operacao = MANUAL
        estado_sistema = MANUAL_NORMAL
        print("Modo alterado: MANUAL")
        print("Controle manual ativo: sinal normal forçado")
    else:
        modo_operacao = AUTOMATICO
        estado_sistema = MONITORANDO
        print("Modo alterado: AUTOMATICO")
        print("Sensor LDR voltou a controlar o sistema")


def atualizar_estado_automatico(valor_luz):
    """Atualiza os estados automáticos conforme a luminosidade."""
    global estado_sistema

    if estado_sistema == MONITORANDO:
        if valor_luz > LIMIAR_ENTRA_ALERTA:
            estado_sistema = ALERTA
            print("ALERTA: baixa luminosidade detectada")

    elif estado_sistema == ALERTA:
        if valor_luz < LIMIAR_SAI_ALERTA:
            estado_sistema = MONITORANDO
            print("Luminosidade restabelecida: MONITORANDO")


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


while True:
    instante_atual = time.ticks_ms()
    luminosidade_atual = ler_sensor_luminosidade()

    tratar_botao(instante_atual)

    if modo_operacao == AUTOMATICO and estado_sistema != OFF:
        atualizar_estado_automatico(luminosidade_atual)

    atualizar_sinalizacao_led(instante_atual)