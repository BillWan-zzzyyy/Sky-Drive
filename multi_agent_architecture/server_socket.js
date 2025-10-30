/**
 * This file boots an HTTP + Socket.IO server for the function of multi-agent communication.
 * 本文件用于启动支持multi_agent功能的 HTTP + Socket.IO 服务。
 *
 */

// -----------------------------
// Config
// -----------------------------
const http = require('http');
const express = require('express');
const { Server: SocketIOServer } = require('socket.io');

/**
 * Configuration
 */
const CONFIG = {
  server: {
    host: process.env.HOST || '192.168.1.1',
    port: Number(process.env.PORT || 3000),
  },
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
  },
  paths: {
    static_dir: 'public',
  },
};


const EVENTS = {
  REGISTER: 'register',
  DISCONNECT: 'disconnect',

  CARLA_DATA: 'carla-data',
  SENSOR_IMAGE: 'sensor-image',
  RADAR_DATA: 'radar-data',

  CLIENT_DISCONNECTED: 'client-disconnected',
};

/**
 * Define different client types
 */
const CLIENT_TYPES = {
  CARLA: 'Carla',
  WEB: 'web',
};

// -----------------------------
// Logger
// -----------------------------

function _ts() {
  return new Date().toISOString();
}
const logger = {
  info: (...args) => console.log(`[INFO ] ${_ts()}`, ...args),
  warn: (...args) => console.warn(`[WARN ] ${_ts()}`, ...args),
  error: (...args) => console.error(`[ERROR] ${_ts()}`, ...args),
  debug: (...args) => (process.env.DEBUG ? console.log(`[DEBUG] ${_ts()}`, ...args) : undefined),
};

// -----------------------------
// Validators
// -----------------------------
/**
 * Validate basic Carla telemetry payload structure.
 * @param {object} data - Expected object
 * @returns {boolean} true if valid
 * @example
 * // Example
 * // is_valid_carla_data({ speed: 10, heading: 1.57 }) -> true
 */
function is_valid_carla_data(data) {
  return data && typeof data === 'object';
}

/**
 * Validate sensor image payload.
 * @param {object} data
 * @returns {boolean}
 * @example
 * // is_valid_sensor_image({ id: 'cam01', image: 'data:image/png;base64,...' }) -> true
 */
function is_valid_sensor_image(data) {
  return Boolean(
    data &&
      typeof data.id === 'string' &&
      typeof data.image === 'string' &&
      data.image.length > 0
  );
}

/**
 * Validate radar payload.
 * @param {object} data
 * @returns {boolean}
 * @example
 * // is_valid_radar_data({ id:'rad01', frame:12, radar_info:{points:[...]}}) -> true
 */
function is_valid_radar_data(data) {
  return Boolean(
    data &&
      typeof data.id === 'string' &&
      Number.isFinite(data.frame) &&
      data.radar_info &&
      typeof data.radar_info === 'object'
  );
}

// -----------------------------
// CarlaRegistry
// -----------------------------

class CarlaRegistry {
  constructor() {
    /** @type {Set<string>} */
    this.ids = new Set();
  }

  /**
   * Add a Carla client by socket id.
   * @param {string} socket_id
   * @example
   * // add
   * // registry.add('abc123')
   */
  add(socket_id) {
    this.ids.add(socket_id);
  }

  /**
   * Remove a Carla client by socket id.
   * @param {string} socket_id
   */
  remove(socket_id) {
    this.ids.delete(socket_id);
  }

  /**
   * Check if a socket id belongs to a Carla client.
   * @param {string} socket_id
   * @returns {boolean}
   * @example
   * // registry.has('abc123') -> true/false
   */
  has(socket_id) {
    return this.ids.has(socket_id);
  }
}

// -----------------------------
// Handlers
// -----------------------------
/**
 * Register handlers for Carla-originated events on a connected socket.
 * @param {import('socket.io').Server} io - Socket.IO server instance
 * @param {import('socket.io').Socket} socket - Connected client's socket
 * @example
 * // register_carla_handlers(io, socket)
 * // After client emits: socket.emit('register', 'Carla')
 */
function register_carla_handlers(io, socket) {
  // carla-data
  socket.on(EVENTS.CARLA_DATA, (data) => {
    if (!is_valid_carla_data(data)) {
      logger.warn(`Invalid CARLA_DATA payload from ${socket.id}`);
      return;
    }
    // Broadcast to all clients.
    io.emit(EVENTS.CARLA_DATA, data);
  });

  // sensor-image
  socket.on(EVENTS.SENSOR_IMAGE, (data) => {
    if (!is_valid_sensor_image(data)) {
      logger.warn(`Invalid SENSOR_IMAGE payload from ${socket.id}`);
      return;
    }
    const { id, image } = data; 
    io.emit(EVENTS.SENSOR_IMAGE, { id, image });
  });

  // radar-data
  socket.on(EVENTS.RADAR_DATA, (data) => {
    if (!is_valid_radar_data(data)) {
      logger.warn(`Invalid RADAR_DATA payload from ${socket.id}`);
      return;
    }
    const { id, frame, radar_info } = data;
    logger.info(`Radar from ${socket.id}: frame=${frame}`);
    io.emit(EVENTS.RADAR_DATA, { id, frame, radar_info });
  });
}

/**
 * Register handlers for Web clients (placeholder for future features).
 * @param {import('socket.io').Server} _io
 * @param {import('socket.io').Socket} _socket
 */
function register_web_handlers(_io, _socket) {
  // Add web-side listeners here as needed.
}

// -----------------------------
// Socket init
// -----------------------------
/**
 * Initialize Socket.IO connection lifecycle and route client types to handlers.
 * @param {import('socket.io').Server} io
 * @param {CarlaRegistry} registry
 */
function init_socket(io, registry) {
  io.on('connection', (socket) => {
    logger.info('Client Connected:', socket.id);

    // Register client type
    socket.on(EVENTS.REGISTER, (client_type) => {
      if (client_type === CLIENT_TYPES.CARLA) {
        registry.add(socket.id);
        logger.info(`Client ${socket.id} is a Carla Client`);
        register_carla_handlers(io, socket);
      } else if (client_type === CLIENT_TYPES.WEB) {
        logger.info(`Client ${socket.id} is a Web Client`);
        register_web_handlers(io, socket);
      } else {
        logger.warn(`Client ${socket.id} registered unknown type:`, client_type);
      }
    });

    // Disconnect handling
    socket.on(EVENTS.DISCONNECT, () => {
      const was_carla = registry.has(socket.id);
      if (was_carla) {
        registry.remove(socket.id);
        logger.info('Carla Client Disconnected:', socket.id);
        io.emit(EVENTS.CLIENT_DISCONNECTED, socket.id);
      } else {
        logger.info('Web Client Disconnected:', socket.id);
      }
    });
  });
}

// -----------------------------
// Server bootstrap
// -----------------------------
/**
 * Start HTTP server
 *
 * @example
 * // node server_socket.js
 *
 * @example
 * // Example
 * // socket.emit('sensor-image', { id:'cam01', image:'data:image/png;base64,...' })
 */
function main() {
  const app = express();
  app.use(express.static(CONFIG.paths.static_dir));

  const server = http.createServer(app);
  const io = new SocketIOServer(server, { cors: { origin: CONFIG.cors.origin } });

  const registry = new CarlaRegistry();
  init_socket(io, registry);

  server.listen(CONFIG.server.port, CONFIG.server.host, () => {
    logger.info(`Socket.IO Server is running at http://${CONFIG.server.host}:${CONFIG.server.port}`);
  });
}

if (require.main === module) {
  main();
}
