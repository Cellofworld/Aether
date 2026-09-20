import Fastify from 'fastify';
import { config } from './config/env';
import { buildApp } from './app';

async function start() {
  const fastify = Fastify({
    logger: {
      level: config.logLevel,
    },
  });
  
  await buildApp(fastify);
  
  try {
    await fastify.listen({ 
      port: config.port, 
      host: config.host 
    });
    
    console.log(`🚀 Aether Media Server running on http://${config.host}:${config.port}`);
    console.log(`📺 API available at http://${config.host}:${config.port}/api`);
    console.log(`🏥 Health check at http://${config.host}:${config.port}/health`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

start();
