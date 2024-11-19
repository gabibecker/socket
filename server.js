const http = require('http');
const { Server } = require('socket.io');

const server = http.createServer();
const io = new Server(server, {
    allowRequest: (req, callback) => {
        const token = req._query.token;
        if (token === 'meu-token-secreto') {
            callback(null, true);
        } else {
            callback('Token inválido. Conexão rejeitada.', false);
        }
    }
});

const connectedClients = {};

io.on('connection', (socket) => {
    console.log(`Cliente conectado: ${socket.id}`);

    // Chat entre clientes
    socket.on('message', ({ to, message }) => {
        if (to === 'all') {
            io.emit('chat-message', { from: connectedClients[socket.id], message });
        } else {
            io.to(to).emit('chat-message', { from: connectedClients[socket.id], message });
        }
    });

    // Comandos entre clientes
    socket.on('command', ({ to, command }) => {
        io.to(to).emit('execute-command', { from: socket.id, command });
    });

    // Easter Eggs
    socket.on('easter-egg', ({ to, action }) => {
        io.to(to).emit('easter-egg-action', { action });
    });

    // WebRTC Sinalização
    socket.on('webrtc-offer', ({ to, offer }) => {
        io.to(to).emit('webrtc-offer', { from: socket.id, offer });
    });
    socket.on('webrtc-answer', ({ to, answer }) => {
        io.to(to).emit('webrtc-answer', { from: socket.id, answer });
    });
    socket.on('webrtc-ice-candidate', ({ to, candidate }) => {
        io.to(to).emit('webrtc-ice-candidate', { from: socket.id, candidate });
    });

    // Instalar Aplicativos
    socket.on('install-app', ({ to, app }) => {
        io.to(to).emit('install-app', { from: socket.id, app });
    });

    socket.on('disconnect', () => {
        console.log(`Cliente desconectado: ${socket.id}`);
        delete connectedClients[socket.id];
        socket.broadcast.emit('client-disconnected', { id: socket.id });
    });
});

server.listen(3000, () => {
    console.log('Servidor rodando na porta 3000');
});