# 📝 Relatório do Candidato

### 👤 Identificação do Candidato

- **Nome completo: Miguel Wagner Galvão Ferreira de Morais**  
- **GitHub: https://github.com/miguelw11/processoseletivoIA-Miguel**  

---

## 1️⃣ Visão Geral da Solução

Este projeto apresenta o desenvolvimento de um sistema embarcado dedicado ao monitoramento inteligente de luminosidade ambiente, utilizando a placa ESP32 como unidade de processamento, um sensor LDR como elemento de aquisição analógica e um LED como atuador de sinalização visual.

A proposta foi construída para simular um cenário real de supervisão luminosa em ambientes que necessitam de acompanhamento contínuo, como:

corredores de circulação;
depósitos técnicos;
salas de equipamentos;
áreas industriais;
ambientes prediais de segurança.

O firmware foi projetado para atuar em dois contextos complementares:

🔹 Modo Automático

O próprio sistema realiza a leitura da luminosidade e toma decisões de forma autônoma, sinalizando condições críticas de baixa iluminação.

🔹 Modo Manual

O operador assume o controle da sinalização, podendo forçar estados normais ou de alerta independentemente da leitura do sensor.

Essa dupla abordagem torna a solução mais robusta, pois não depende exclusivamente da automação: em cenários de manutenção, contingência, falha do sensor ou testes operacionais, o usuário pode intervir diretamente.

Em sistemas embarcados reais, essa coexistência entre operação automática e controle manual é amplamente utilizada para garantir:

-Redundância operacional

-Segurança em inspeções

-Validação de componentes

-Resposta humana em situações excepcionais

### ⏺️Cenário real de aplicação

<div align="center">

<img width="641" height="424" alt="image" src="https://github.com/user-attachments/assets/5d5acc87-bab5-4351-b3d3-845291e82193" />


</div>

O sistema proposto seria ideal em locais nos quais a queda de luminosidade pode representar risco operacional, dificuldade de circulação, falhas de inspeção visual, comprometimento de manutenção ou aumento da insegurança em áreas técnicas.

Dessa forma, a solução atua como um núcleo de supervisão preventiva, permitindo que empresas implementem sinalização rápida e de baixo custo para ambientes críticos.


---

## 2️⃣ Arquitetura do Sistema Embarcado

A lógica do firmware foi estruturada utilizando máquina de estados finitos, o que proporciona previsibilidade de execução, código modular, facilidade de manutenção e possibilidade de expansão futura.

### ⏺️Fluxo principal do `main.py`

O laço principal executa continuamente:

1. leitura do tempo atual (`ticks_ms()`);
2. leitura analógica do sensor LDR;
3. tratamento dos eventos do botão;
4. atualização dos estados automáticos quando aplicável;
5. atualização da sinalização visual do LED.

Essa abordagem evita travamentos e mantém o firmware responsivo.

### ⏺️Estrutura lógica resumida

Inicialização -> OFF
      |
Clique curto
      v
AUTOMATICO / MONITORANDO
      |
Baixa luminosidade
      v
ALERTA

Clique longo <-> alterna AUTOMATICO / MANUAL

MANUAL:
clique curto alterna MANUAL_NORMAL <-> MANUAL_ALERTA

MANUAL:
clique curto alterna MANUAL_NORMAL <-> MANUAL_ALERTA

### ⏺️Estados implementados
**OFF** → sistema desligado;

**MONITORANDO** → luminosidade adequada;

**ALERTA** → baixa luminosidade detectada automaticamente;

**MANUAL_NORMAL** → sinal normal forçado pelo operador;

**MANUAL_ALERTA** → alerta forçado manualmente.

---

## 3️⃣ Componentes Utilizados na Simulação

### ESP32 DevKit V1

-Microcontrolador principal responsável pelo processamento da lógica embarcada.

### Sensor LDR

-Responsável pela aquisição analógica da luminosidade ambiente através do ADC no GPIO34.

### Push Button

-Responsável por toda a interação física com o usuário:

- clique curto;
- clique longo;
- alternância de estados.

### LED Vermelho + Resistor de 220Ω

Atuador visual responsável pela sinalização:

- desligado = OFF;
- aceso fixo = condição normal;
- piscando = condição de alerta.

### Monitor Serial

Exibe logs de transição e monitoramento interno do firmware.

---

## 4️⃣ Decisões Técnicas Relevantes

Durante o desenvolvimento, foram adotadas decisões que aproximam a solução de um firmware profissional.

### ✔ Código modularizado por funções

O código foi separado em funções específicas para leitura do sensor, tratamento do botão, atualização automática de estado e controle do LED.

### ✔ Máquina de estados

A lógica foi organizada por estados explícitos, evitando condicionais confusas e facilitando futuras expansões.

### ✔ Debounce por software

Foi implementado debounce temporal para evitar múltiplas leituras falsas do botão.

### ✔ Clique curto e clique longo

Com apenas um botão físico, o sistema consegue diferenciar comandos simples e comandos de troca de modo.

### ✔ Temporização não bloqueante

A piscagem do LED ocorre com `ticks_ms()`, sem congelar o loop principal.

### ✔ Histerese no sensor

Dois limiares foram aplicados para evitar oscilação instável entre estados.

### ✔ Inclusão do modo manual como redundância operacional

O modo manual não foi inserido apenas como recurso extra, mas como mecanismo de contingência.

Em aplicações reais, sistemas totalmente automáticos podem sofrer falha de sensor, necessidade de manutenção, testes de bancada ou necessidade de inspeção humana.

Com o modo manual, o operador mantém capacidade de:

- validar o atuador;
- forçar sinalização de alerta;
- forçar sinalização normal;
- manter o sistema útil mesmo com falhas de leitura.

Isso agrega valor prático e demonstra preocupação com confiabilidade operacional.

---

## 5️⃣ Resultados Obtidos

Ao final da implementação, a simulação apresentou:

- leitura estável do sensor LDR;
- identificação correta de baixa luminosidade;
- alternância funcional entre OFF, MONITORANDO e ALERTA;
- reconhecimento de clique curto e clique longo;
- alternância entre modos AUTOMÁTICO e MANUAL;
- forçamento manual de estados;
- sinalização visual consistente;
- mensagens de log no terminal serial;
- execução validada com sucesso no GitHub Actions.

A solução se mostrou estável no Wokwi e compatível com execução via VSCode.

---

## 6️⃣ Diagrama no Wokwi

<div align="center">

<img width="674" height="396" alt="image" src="https://github.com/user-attachments/assets/b6ca462e-9cee-4e5e-bae0-4f4cd8dbe2ad" />

</div> 

---

## 7️⃣ Execução Local no VSCode e Geração do `fs.bin`

Para funcionamento local no VSCode com a extensão do Wokwi Simulator, foi utilizada a geração de um filesystem binário (`fs.bin`) contendo os arquivos presentes na pasta `src`.

### Script utilizado: `build_fs.py`

Esse script percorre automaticamente os arquivos da pasta `src`, empacota o conteúdo em um filesystem LittleFS e gera o binário `fs.bin`, utilizado pelo ESP32 durante a simulação.

Sempre que houver alteração em `src/main.py`, execute:

`python build_fs.py`

---

## 8️⃣ Como testar em outra máquina

Para testar em outras máquinas, é necessário seguir alguns passos:

1-Clonar o repositório na IDE

2-Instalar a dependência necessária (pip install littlefs-python)

3-Gerar o filesystem binário (build_fs.py)

4-Configurar Token do Wokwi CI

5-Abrir no VSCode com a extensão Wokwi Simulator

---
---

## 9️⃣ Comentários Finais

O principal aprendizado deste desafio esteve na construção de um firmware orientado a eventos, modular, responsivo e preparado para múltiplos cenários operacionais.

Além da simulação funcional, o projeto buscou reproduzir preocupações reais de engenharia, como:

redundância de operação;
clareza de estados;
manutenção futura;
validação serial;
integração com pipeline automatizado.

Com mais tempo, melhorias futuras incluiriam:

display LCD de status;
buzzer de alerta;
registro histórico de eventos;
monitoramento remoto em nuvem.

---

*Relatório final desenvolvido para o desafio técnico de IoT para o processo seletivo do PNAAT.*
