# 📝 Relatório do Candidato

### 👤 Identificação do Candidato

- **Nome completo: Miguel Wagner Galvão Ferreira de Morais**  
- **GitHub: https://github.com/miguelw11/processoseletivoIoT-Miguel**  

---

## 1️⃣ Visão Geral da Solução

Este projeto apresenta um sistema embarcado simulado para **monitoramento inteligente de luminosidade em ambientes críticos**, utilizando ESP32, sensor LDR, LED de sinalização e integração com Telegram.

A solução identifica situações de baixa luminosidade, sinaliza localmente por meio de LED e permite o acompanhamento remoto pelo Telegram, com notificações automáticas, comandos de controle e consulta ao histórico de eventos.

O sistema foi pensado para ambientes onde a iluminação influencia diretamente a segurança, a manutenção ou a operação, como:

- corredores de circulação;
- salas técnicas;
- depósitos;
- áreas industriais;
- ambientes prediais de segurança.

A operação pode ocorrer em dois modos:

| Modo | Descrição |
|---|---|
| **Automático** | O ESP32 lê o sensor LDR e decide quando entrar em estado de alerta. |
| **Manual** | O operador pode forçar estados de normalidade ou alerta, seja pelo botão físico ou remotamente pelo Telegram. |

Além da atuação local, o projeto possui uma camada IoT de supervisão remota. Por meio do bot no Telegram, o usuário pode ligar ou desligar o sistema, consultar status, alternar modos, forçar alerta, normalizar a sinalização e visualizar os últimos eventos registrados.

Essa combinação entre **monitoramento automático**, **controle manual** e **comunicação remota** aproxima a solução de um produto aplicável em cenários reais, nos quais é importante detectar falhas de iluminação, reduzir riscos operacionais e permitir resposta rápida mesmo à distância.

### ⏺️Cenário real de aplicação

<div align="center">

<img width="641" height="424" alt="image" src="https://github.com/user-attachments/assets/5d5acc87-bab5-4351-b3d3-845291e82193" />

</div>

O sistema proposto seria ideal em locais nos quais a queda de luminosidade pode representar risco operacional, dificuldade de circulação, falhas de inspeção visual, comprometimento de manutenção ou aumento da insegurança em áreas técnicas.

Dessa forma, a solução atua como um núcleo de supervisão preventiva, permitindo que empresas implementem sinalização rápida e de baixo custo para ambientes críticos.

---

## 2️⃣ Arquitetura do Sistema Embarcado

A lógica do firmware foi organizada em torno de uma **máquina de estados finitos**, com leitura contínua do sensor LDR, tratamento de botão físico, controle do LED e integração opcional com Telegram.

O objetivo da arquitetura é manter o sistema responsivo, previsível e fácil de expandir, evitando travamentos por `sleep` bloqueante no loop principal.

### Fluxo principal do `main.py`

O laço principal executa continuamente as etapas abaixo:

| Etapa | Responsabilidade |
|---|---|
| 1. Tempo do sistema | Captura o instante atual com `ticks_ms()` para permitir debounce, clique longo e temporizações não bloqueantes. |
| 2. Leitura do LDR | Realiza a leitura analógica da luminosidade no GPIO34. |
| 3. Tratamento do botão | Identifica clique curto e clique longo para ligar/desligar ou alternar modos. |
| 4. Máquina de estados | Atualiza o estado do sistema conforme modo automático, modo manual ou luminosidade detectada. |
| 5. Telegram | Verifica periodicamente comandos remotos e envia notificações em eventos relevantes. |
| 6. Registro de eventos | Armazena os últimos eventos importantes para consulta posterior. |
| 7. Sinalização visual | Atualiza o LED conforme o estado atual do sistema. |


> `(*)` A integração com Telegram é ativada apenas quando existe um `config.py` local com as credenciais do bot. No GitHub Actions, o firmware executa sem credenciais, mantendo a validação segura.

### Máquina de estados

| Estado | Descrição | Saída visual |
|---|---|---|
| `OFF` | Sistema desligado | LED apagado |
| `MONITORANDO` | Sistema ativo em modo automático | LED aceso fixo |
| `ALERTA` | Baixa luminosidade detectada | LED piscando |
| `MANUAL_NORMAL` | Estado normal forçado pelo operador | LED aceso fixo |
| `MANUAL_ALERTA` | Alerta forçado manualmente | LED piscando |

### Modos de operação

| Modo | Como funciona |
|---|---|
| `AUTOMATICO` | O sensor LDR controla a transição entre monitoramento e alerta. |
| `MANUAL` | O operador força o estado normal ou de alerta, independentemente do sensor. |

### Interações disponíveis

| Origem da interação | Ação possível |
|---|---|
| Botão físico — clique curto | Liga/desliga o sistema ou alterna estado manual |
| Botão físico — clique longo | Alterna entre modo automático e modo manual |
| Telegram | Liga/desliga, consulta status, altera modo, força alerta, normaliza e lista eventos |
| Sensor LDR | Aciona alerta automaticamente conforme os limiares de luminosidade |

### Comunicação remota

A comunicação com Telegram foi integrada ao firmware como uma camada de supervisão remota. O sistema consulta novos comandos em intervalos definidos, evitando excesso de requisições e mantendo o loop principal leve.

As notificações são enviadas apenas em eventos relevantes, como:

- sistema iniciado;
- alerta de baixa luminosidade;
- luminosidade restabelecida;
- alteração de modo;
- comandos remotos executados;
- desligamento remoto.

Essa estrutura evita spam de mensagens e aproxima o projeto de um comportamento mais realista para aplicações IoT.

---

## 3️⃣ Componentes Utilizados

| Componente | Função no Projeto |
|---|---|
| ESP32 DevKit V1 | Microcontrolador responsável pela execução do firmware |
| Sensor LDR | Mede a luminosidade ambiente por leitura analógica no GPIO34 |
| Push Button | Permite interação física com clique curto e clique longo |
| LED Vermelho | Sinaliza estado normal ou alerta |
| Resistor 220Ω | Protege o LED contra excesso de corrente |
| Monitor Serial | Exibe logs de inicialização, eventos e transições |
| Telegram Bot | Permite notificações automáticas e comandos remotos |

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

Ao final do desenvolvimento, o sistema apresentou funcionamento correto na simulação do Wokwi e foi validado pelo pipeline do GitHub Actions.

Os principais resultados foram:

| Recurso | Resultado |
|---|---|
| Leitura do LDR | O sensor responde à variação de luminosidade na simulação. |
| Máquina de estados | O sistema alterna corretamente entre `OFF`, `MONITORANDO`, `ALERTA`, `MANUAL_NORMAL` e `MANUAL_ALERTA`. |
| Modo automático | A luminosidade é monitorada pelo LDR e o alerta é acionado conforme os limiares definidos. |
| Modo manual | O operador consegue forçar estado normal ou alerta, independentemente do sensor. |
| Botão físico | Clique curto e clique longo funcionam com debounce. |
| LED de sinalização | LED apagado em `OFF`, aceso fixo em estado normal e piscando em alerta. |
| Telegram | Notificações automáticas, comandos remotos e consulta de eventos funcionam localmente. |
| Registro de eventos | O sistema armazena e exibe os últimos eventos relevantes. |
| GitHub Actions | A simulação é executada automaticamente sem expor credenciais reais. |

### Comportamento observado

Na simulação, o sistema inicia em estado `OFF`. Ao ser ligado, entra em modo de monitoramento e passa a avaliar continuamente a luminosidade do ambiente.

Quando a luminosidade atinge o limite crítico configurado, o firmware altera o estado para `ALERTA`, faz o LED piscar e registra o evento. Quando a luminosidade retorna para a faixa considerada segura, o sistema volta para `MONITORANDO`.

Além do controle físico pelo botão, o sistema também pôde ser controlado remotamente pelo Telegram, permitindo ligar, desligar, consultar status, alternar modo de operação, forçar alerta e visualizar eventos.

A validação no GitHub Actions foi mantida de forma segura: o firmware executa sem as credenciais reais do Telegram no ambiente de CI, mas preserva toda a lógica principal da simulação.

---

## 6️⃣ Demonstração do Funcionamento

### Circuito no Wokwi

A simulação foi montada no Wokwi utilizando ESP32, sensor LDR, botão físico e LED de sinalização. O circuito representa um sistema embarcado simples, mas funcional, capaz de monitorar luminosidade, sinalizar alertas e receber comandos físicos ou remotos.

<div align="center">

<img width="674" height="396" alt="image" src="https://github.com/user-attachments/assets/b6ca462e-9cee-4e5e-bae0-4f4cd8dbe2ad" />

</div> 

---

### Integração com Telegram

Além da sinalização local pelo LED, o sistema também possui integração com Telegram, permitindo que o operador acompanhe e controle o sistema remotamente.

Através do bot, é possível consultar o estado atual, alternar modos de operação, forçar alerta, desligar o sistema e visualizar os últimos eventos registrados.

<div align="center">
      
<img width="1015" height="623" alt="image" src="https://github.com/user-attachments/assets/55293af8-510b-44da-8af3-6c8b662fcfae" />

</div>

---

### Controle Remoto do Sistema

O bot aceita comandos remotos como `/manual`, `/auto`, `/forcar_alerta`, `/normal`, `/status`, `/ligar` e `/desligar`.

Isso transforma o projeto em uma solução mais próxima de um produto IoT real, pois o operador não precisa estar fisicamente próximo do dispositivo para acompanhar ou alterar seu funcionamento.

<div align="center">

<img width="1018" height="631" alt="image" src="https://github.com/user-attachments/assets/9ae97f5d-942f-4b29-8efc-a71128d47402" />

</div>

---

### Registro de Eventos

O firmware mantém um histórico dos últimos eventos relevantes, permitindo consultar ações recentes diretamente pelo Telegram.

Esse recurso é útil para inspeção, manutenção e acompanhamento operacional, pois permite verificar rapidamente se houve alerta de luminosidade, alteração de modo ou desligamento remoto.

<div align="center">

<img width="677" height="477" alt="image" src="https://github.com/user-attachments/assets/1efcaff9-0149-4187-a606-a888b2314935" />

</div>

---

## 7️⃣ Execução Local no VSCode e Geração do `fs.bin`

Para funcionamento local no VSCode com a extensão do Wokwi Simulator, foi utilizada a geração de um filesystem binário (`fs.bin`) contendo os arquivos presentes na pasta `src`.

### Script utilizado: `build_fs.py`

Esse script percorre automaticamente os arquivos da pasta `src`, empacota o conteúdo em um filesystem LittleFS e gera o binário `fs.bin`, utilizado pelo ESP32 durante a simulação.

Sempre que houver alteração em `src/main.py`, execute:

`python build_fs.py`

---

## 8️⃣ Como Testar o Projeto em Outra Máquina

O projeto pode ser executado de duas formas:

| Modo | Descrição |
|---|---|
| **Padrão / CI** | Executa a simulação sem Telegram, usado pelo GitHub Actions. |
| **Local com Telegram** | Executa a simulação com notificações e comandos remotos, usando `src/config.py`. |

---

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Instalar dependência

```bash
pip install littlefs-python
```

### 3. Gerar o `fs.bin`

Sempre que alterar arquivos em `src/`, gere novamente o filesystem:

```bash
python build_fs.py
```

Resultado esperado:

```text
+ config.example.py
- ignorado: config.py
+ main.py
fs.bin atualizado com sucesso!
```

O `config.py` é ignorado para evitar exposição de tokens.

### 4. Rodar no VSCode com Wokwi

1. Abra a pasta raiz do projeto no VSCode.
2. Confirme que existem `wokwi.toml`, `diagram.json` e `fs.bin`.
3. Inicie a simulação pela extensão Wokwi Simulator.
4. Observe os logs no terminal serial.

### 5. Teste Local com Telegram

Para ativar o Telegram localmente, crie o arquivo:

```text
src/config.py
```

com:

```python
TELEGRAM_TOKEN = "COLE_SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "COLE_SEU_CHAT_ID_AQUI"
```

Esse arquivo contém credenciais reais e **por isso não consta no GitHub**.

---

## 9️⃣ Comentários Finais

Este projeto evoluiu de uma simulação simples de luminosidade para uma solução IoT mais completa, com monitoramento local, controle manual, notificações remotas via Telegram e validação automatizada pelo GitHub Actions.

Durante o desenvolvimento, os principais aprendizados foram:

- construção de firmware orientado a eventos;
- uso de máquina de estados finitos;
- aplicação de temporização não bloqueante;
- tratamento de botão com clique curto, clique longo e debounce;
- integração segura com Telegram sem exposição de tokens;
- geração de filesystem com `fs.bin` para simulação no Wokwi;
- validação automática da execução pelo pipeline de CI.

Além da parte técnica, o projeto buscou reproduzir preocupações reais de engenharia, como:

- operação automática com possibilidade de intervenção manual;
- registro dos últimos eventos do sistema;
- separação entre execução local com Telegram e validação segura no CI;
- resposta visual imediata por LED;
- possibilidade de expansão para cenários empresariais.

Com mais tempo, melhorias futuras poderiam incluir:

| Melhoria | Benefício |
|---|---|
| Display LCD/OLED | Exibir modo, estado e luminosidade diretamente no dispositivo |
| Buzzer de alerta | Adicionar sinalização sonora em situações críticas |
| Dashboard web | Permitir acompanhamento visual por navegador |
| Armazenamento em nuvem | Manter histórico persistente de eventos |
| MQTT | Integrar o sistema a plataformas IoT e automação predial |
| Múltiplos sensores | Monitorar diferentes pontos de um mesmo ambiente |

De forma geral, a solução demonstra como um sistema embarcado simples pode ser expandido para um produto IoT funcional, combinando sensores, atuadores, lógica robusta, comunicação remota e uma qualidade de segurança.

---

*Relatório final desenvolvido para o desafio técnico de IoT para o processo seletivo do PNAAT.*
