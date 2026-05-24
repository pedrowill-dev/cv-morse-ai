import cv2
import mediapipe as mp
import time
import platform
import subprocess

mp_face_mesh = mp.solutions.face_mesh

MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z",
    "-----": "0", ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9",
}

# Índices MediaPipe FaceMesh
INDICES_OLHO_ESQUERDO = [33, 160, 158, 133, 153, 144]
INDICES_OLHO_DIREITO = [362, 385, 387, 263, 373, 380]

LIMITE_OLHO_FECHADO = 0.20
DURACAO_PISCADA_LONGA = 0.30
PAUSA_LETRA = 1.5
PAUSA_PALAVRA = 4.0


def razao_aspecto_olho(landmarks, indices, largura, altura):
    pontos = []
    for i in indices:
        p = landmarks[i]
        pontos.append((int(p.x * largura), int(p.y * altura)))

    horizontal = abs(pontos[0][0] - pontos[3][0])
    vertical1 = abs(pontos[1][1] - pontos[5][1])
    vertical2 = abs(pontos[2][1] - pontos[4][1])
    return (vertical1 + vertical2) / (2.0 * horizontal)


def centro_olho(landmarks, indices, largura, altura):
    x_total = 0
    y_total = 0
    for i in indices:
        p = landmarks[i]
        x_total += int(p.x * largura)
        y_total += int(p.y * altura)
    return x_total // len(indices), y_total // len(indices)


def tocar_bipe(curto=True):
    sistema = platform.system()
    if sistema == "Windows":
        import winsound
        frequencia = 800
        duracao_ms = 120 if curto else 300
        winsound.Beep(frequencia, duracao_ms)
    elif sistema == "Darwin":
        arquivo = "/System/Library/Sounds/Glass.aiff" if curto else "/System/Library/Sounds/Pop.aiff"
        subprocess.Popen(["afplay", arquivo])
    else:
        print("\a", end="", flush=True)


def desenhar_medidor(frame, x, y, largura, altura, proporcao, texto):
    x = int(x)
    y = int(y)
    proporcao = max(0.0, min(proporcao, 1.0))
    cor_fundo = (50, 50, 50)
    cor_borda = (255, 255, 255)
    cor_preenchimento = (0, 220, 255) if proporcao < 1.0 else (0, 200, 0)

    cv2.rectangle(frame, (x, y), (x + largura, y + altura), cor_fundo, -1)
    cv2.rectangle(frame, (x, y), (x + largura, y + altura), cor_borda, 2)
    cv2.rectangle(frame, (x + 2, y + 2),
                  (x + 2 + int((largura - 4) * proporcao), y + altura - 2),
                  cor_preenchimento, -1)
    cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA)


cap = cv2.VideoCapture(0)

codigo_morse_atual = ""
texto_decodificado = ""

inicio_fechamento = None
ultimo_tempo_entrada = time.time()

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as malha_face:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        altura, largura, _ = frame.shape
        imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = malha_face.process(imagem_rgb)
        agora = time.time()

        if resultados.multi_face_landmarks:
            pontos_face = resultados.multi_face_landmarks[0].landmark
            ear_esquerdo = razao_aspecto_olho(pontos_face, INDICES_OLHO_ESQUERDO, largura, altura)
            ear_direito = razao_aspecto_olho(pontos_face, INDICES_OLHO_DIREITO, largura, altura)

            olho_esquerdo_fechado = ear_esquerdo < LIMITE_OLHO_FECHADO
            olho_direito_fechado = ear_direito < LIMITE_OLHO_FECHADO
            olhos_fechados = olho_esquerdo_fechado or olho_direito_fechado

            if olhos_fechados:
                if inicio_fechamento is None:
                    inicio_fechamento = agora
                tempo_fechado = agora - inicio_fechamento
            else:
                tempo_fechado = 0.0
                if inicio_fechamento is not None:
                    duracao = agora - inicio_fechamento
                    if duracao >= 0.05:
                        if duracao < DURACAO_PISCADA_LONGA:
                            codigo_morse_atual += "."
                            tocar_bipe(curto=True)
                        else:
                            codigo_morse_atual += "-"
                            tocar_bipe(curto=False)
                        ultimo_tempo_entrada = agora
                    inicio_fechamento = None

            texto_olho_esquerdo = f"EAR {ear_esquerdo:.2f}"
            texto_olho_direito = f"EAR {ear_direito:.2f}"
            cx_esq, cy_esq = centro_olho(pontos_face, INDICES_OLHO_ESQUERDO, largura, altura)
            cx_dir, cy_dir = centro_olho(pontos_face, INDICES_OLHO_DIREITO, largura, altura)

            proporcao = 0.0
            if inicio_fechamento is not None:
                proporcao = min((agora - inicio_fechamento) / DURACAO_PISCADA_LONGA, 1.0)

            cv2.putText(frame, texto_olho_esquerdo, (cx_esq - 40, cy_esq - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, texto_olho_direito, (cx_dir - 40, cy_dir - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.circle(frame, (cx_esq, cy_esq), 5, (0, 255, 0), -1)
            cv2.circle(frame, (cx_dir, cy_dir), 5, (0, 255, 0), -1)

            desenhar_medidor(frame, cx_esq - 70, cy_esq + 20, 140, 18, proporcao, "Fechamento")
            desenhar_medidor(frame, cx_dir - 70, cy_dir + 20, 140, 18, proporcao, "Fechamento")

        if codigo_morse_atual and agora - ultimo_tempo_entrada > PAUSA_LETRA:
            texto_decodificado += MORSE.get(codigo_morse_atual, "?")
            codigo_morse_atual = ""
            ultimo_tempo_entrada = agora

        if texto_decodificado and agora - ultimo_tempo_entrada > PAUSA_PALAVRA:
            if not texto_decodificado.endswith(" "):
                texto_decodificado += " "
                ultimo_tempo_entrada = agora

        cv2.putText(frame, f"Morse: {codigo_morse_atual}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Texto: {texto_decodificado}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, "Pressione Q para sair, B para apagar, C para limpar", (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Morse pelos olhos", frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break
        if tecla == ord("b"):
            texto_decodificado = texto_decodificado[:-1]
        if tecla == ord("c"):
            codigo_morse_atual = ""
            texto_decodificado = ""
            inicio_fechamento = None

cap.release()
cv2.destroyAllWindows()
