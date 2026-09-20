import { FastifyInstance } from 'fastify';
import { config } from './config/env';
import { prisma } from './config/database';
import { setupAuthDecorators } from './middleware/auth';
import { authRoutes } from './routes/auth';
import { libraryRoutes } from './routes/library';
import { mediaRoutes } from './routes/media';
import { playbackRoutes } from './routes/playback';
import { searchRoutes } from './routes/search';
import { adminRoutes } from './routes/admin';

export async function buildApp(fastify: FastifyInstance) {
  // Register JWT
  fastify.register(require('@fastify/jwt'), {
    secret: config.jwtSecret,
    sign: {
      expiresIn: '7d',
    },
  });
  
  // Setup auth decorators
  setupAuthDecorators(fastify);
  
  // Register CORS
  fastify.register(require('@fastify/cors'), {
    origin: config.corsOrigins.includes('*') ? true : config.corsOrigins,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
  });
  
  // Health check
  fastify.get('/health', async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });
  
  // API Routes - Auth (public)
  fastify.register(async (app) => {
    app.register(authRoutes, { prefix: '/auth' });
  }, { prefix: '/api' });
  
  // API Routes - Protected
  fastify.register(async (app) => {
    app.register(libraryRoutes, { prefix: '/libraries' });
    app.register(mediaRoutes, { prefix: '' });
    app.register(playbackRoutes, { prefix: '/playback' });
    app.register(searchRoutes, { prefix: '/search' });
    app.register(adminRoutes, { prefix: '/admin' });
  }, { prefix: '/api' });
  
  // Error handler
  fastify.setErrorHandler((error, request, reply) => {
    fastify.log.error(error);
    
    if (error.validation) {
      reply.code(400).send({ 
        error: 'Validation Error', 
        message: error.message,
        details: error.validation 
      });
    } else {
      reply.code(error.statusCode || 500).send({ 
        error: error.name, 
        message: error.message 
      });
    }
  });
  
  // Graceful shutdown
  const onClose = async () => {
    await prisma.$disconnect();
  };
  
  fastify.addHook('onClose', onClose);
}
