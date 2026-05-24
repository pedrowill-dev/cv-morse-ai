# Código Morse pelos Olhos

Projeto em Python usando **OpenCV** e **MediaPipe** para detectar piscadas e transformar o tempo de fechamento dos olhos em Código Morse.

## Ideia

O sistema usa a câmera para detectar os olhos em tempo real.

A lógica é baseada no tempo em que o olho fica fechado:

- Piscada curta = ponto `.`
- Piscada longa = barra `-`

Exemplo:

```txt
... --- ...
````

Resultado:

```txt
SOS
```

## Tecnologias usadas

* Python
* OpenCV
* MediaPipe
* Time
* Platform
* Subprocess

## Instalação

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente:

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como executar

Salve o código principal em um arquivo, por exemplo:

```bash
main.py
```

Execute:

```bash
python main.py
```

## Como usar

1. Abra o programa.
2. A câmera será iniciada.
3. Feche o olho rapidamente para gerar um ponto `.`
4. Mantenha o olho fechado por mais tempo para gerar uma barra `-`
5. Aguarde uma pequena pausa para o sistema formar a letra.
6. O texto decodificado será exibido na tela.

## Controles

| Tecla | Ação                    |
| ----- | ----------------------- |
| `q`   | Sair                    |
| `c`   | Limpar texto            |
| `b`   | Apagar último caractere |

## Exemplo de uso

Para escrever `SOS`:

```txt
S = ...
O = ---
S = ...
```

Então você deve piscar:

```txt
curto curto curto
longo longo longo
curto curto curto
```

## Som

O sistema pode emitir sons diferentes para cada símbolo:

* Ponto `.` = beep curto
* Barra `-` = beep longo

Em alguns sistemas, o som pode usar comandos nativos do sistema operacional.

## Observação

A precisão depende de:

* iluminação do ambiente
* posição do rosto
* qualidade da câmera
* distância da câmera
* ajuste do limite de detecção dos olhos

Caso detecte errado, ajuste os valores de tempo e sensibilidade no código.

## Objetivo

Este projeto demonstra uma forma simples de comunicação usando apenas os olhos, combinando:

* visão computacional
* acessibilidade
* código morse
* Python
* OpenCV

```
```
