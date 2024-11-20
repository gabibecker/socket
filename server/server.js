const http = require('http');
const { Server } = require('socket.io');

// Criação do servidor HTTP
const server = http.createServer();

// Configuração do Socket.IO com autenticação
const io = new Server(server, {
    allowRequest: (req, callback) => {
        // Valida o token enviado no cabeçalho Authorization
        const token = req.headers.authorization; // Extrai o token
        if (token === 'meu-token-secreto') {
            callback(null, true); // Permite conexão
        } else {
            callback('Token inválido. Conexão rejeitada.', false); // Rejeita conexão
        }
    }
});

// Lista de clientes conectados
const connectedClients = {};

// Configuração de eventos do Socket.IO
io.on('connection', (socket) => {
    console.log(`Cliente conectado: ${socket.id}`);
    connectedClients[socket.id] = { id: socket.id };

    // Notifica todos os clientes sobre um novo cliente conectado
    socket.broadcast.emit('client-connected', { id: socket.id });

    // Gerenciamento de mensagens (chat)
    socket.on('message', ({ to, message }) => {
        if (to === 'all') {
            io.emit('chat-message', { from: socket.id, message }); // Mensagem pública
        } else {
            io.to(to).emit('chat-message', { from: socket.id, message }); // Mensagem privada
        }
    });

    // Comandos entre clientes
    socket.on('command', ({ to, command }) => {
        io.to(to).emit('execute-command', { from: socket.id, command });
    });

    // Sinalização WebRTC
    socket.on('webrtc-offer', ({ to, offer }) => {
        io.to(to).emit('webrtc-offer', { from: socket.id, offer });
    });

    socket.on('webrtc-answer', ({ to, answer }) => {
        io.to(to).emit('webrtc-answer', { from: socket.id, answer });
    });

    socket.on('webrtc-ice-candidate', ({ to, candidate }) => {
        io.to(to).emit('webrtc-ice-candidate', { from: socket.id, candidate });
    });

    // Evento de desconexão
    socket.on('disconnect', () => {
        console.log(`Cliente desconectado: ${socket.id}`);
        delete connectedClients[socket.id];
        socket.broadcast.emit('client-disconnected', { id: socket.id });
    });
});

// Inicia o servidor escutando em todas as interfaces de rede
server.listen(3000, '0.0.0.0', () => {
    console.log('Servidor rodando na porta 3000');
});
