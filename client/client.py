import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import socketio
import pyautogui
import screen_brightness_control as sbc
from aiortc import RTCPeerConnection, VideoStreamTrack
import cv2
import asyncio
import os

# Configurações do WebRTC
peer_connection = RTCPeerConnection()
sio = socketio.Client()

def start_server():
    """Função para iniciar o servidor Node.js."""
    try:
        # Caminho para o arquivo do servidor Node.js
        server_path = os.path.join(os.getcwd(), "server", "server.js")
        subprocess.run(["node", server_path])
    except Exception as e:
        print(f"Erro ao iniciar o servidor Node.js: {e}")

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Socket Client")
        self.root.geometry("600x500")

        # Lista de clientes conectados
        self.connected_clients = tk.Listbox(self.root, height=10, width=30)
        self.connected_clients.grid(row=0, column=0, padx=10, pady=10)

        # Área de mensagens
        self.chat_display = tk.Text(self.root, height=20, width=40, state='disabled')
        self.chat_display.grid(row=0, column=1, padx=10, pady=10)

        # Entrada de mensagens
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.grid(row=1, column=1, padx=10, pady=5)

        # Botão de envio
        self.send_button = tk.Button(self.root, text="Enviar Mensagem", command=self.send_message)
        self.send_button.grid(row=2, column=1, pady=5)

        # Botão de comandos
        self.command_button = tk.Button(self.root, text="Executar Comando", command=self.send_command)
        self.command_button.grid(row=3, column=1, pady=5)

        # Botão de transmissão de vídeo
        self.video_button = tk.Button(self.root, text="Iniciar Vídeo", command=self.start_video)
        self.video_button.grid(row=4, column=1, pady=5)

        # Conectar ao servidor
        self.connect_to_server()

    def connect_to_server(self):
        try:
            # Substitua '192.168.x.x' pelo IP do computador que está rodando o servidor
            sio.connect('http://192.168.0.105:3000', headers={'Authorization': '12'})
            messagebox.showinfo("Conexão", "Conectado ao servidor!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao conectar: {e}")

    def send_message(self):
        to = "all"  # Enviar para todos por padrão
        message = self.message_entry.get()
        if message.strip():
            sio.emit('message', {'to': to, 'message': message})
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"Você: {message}\n")
            self.chat_display.config(state='disabled')
            self.message_entry.delete(0, tk.END)

    def send_command(self):
        command = "invert-mouse"  # Comando fixo para teste
        selected_client = self.connected_clients.get(tk.ACTIVE)
        if selected_client:
            sio.emit('command', {'to': selected_client, 'command': command})

    def start_video(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Transmissão de Vídeo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def add_client_to_list(self, client_id):
        self.connected_clients.insert(tk.END, client_id)

    def display_message(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state='disabled')

# Eventos do Socket.IO
@sio.event
def connect():
    print("Conectado ao servidor!")

@sio.on('chat-message')
def on_chat_message(data):
    app.display_message(data['from'], data['message'])

@sio.on('client-connected')
def on_client_connected(data):
    app.add_client_to_list(data['id'])

@sio.on('execute-command')
def on_execute_command(data):
    command = data['command']
    if command == 'invert-mouse':
        pyautogui.moveRel(-100, -100)
    elif command == 'limit-mouse':
        pyautogui.moveTo(500, 500)
    elif command == 'shutdown-monitor':
        sbc.set_brightness(0)
    else:
        print(f"Comando desconhecido: {command}")

def start_client():
    """Função para iniciar a interface gráfica do cliente."""
    root = tk.Tk()
    global app
    app = ClientApp(root)
    root.mainloop()

# Iniciar servidor e cliente ao mesmo tempo
if __name__ == "__main__":
    # Criar uma thread para o servidor
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Iniciar o cliente
    start_client()
