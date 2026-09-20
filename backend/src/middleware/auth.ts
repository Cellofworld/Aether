import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';

export function setupAuthDecorators(fastify: FastifyInstance) {
  fastify.decorate('authenticate', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid or missing token' });
    }
  });
  
  fastify.decorate('adminAuth', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      await request.jwtVerify();
      if (request.user && request.user.role !== 'ADMIN') {
        reply.code(403).send({ error: 'Forbidden', message: 'Admin access required' });
      }
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid or missing token' });
    }
  });
}
