import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';

declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
    adminAuth: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
  }
  
  interface FastifyRequest {
    user: {
      id: string;
      email: string;
      username: string;
      role: 'ADMIN' | 'USER';
    };
  }
}

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
      if (request.user.role !== 'ADMIN') {
        reply.code(403).send({ error: 'Forbidden', message: 'Admin access required' });
      }
    } catch (err) {
      reply.code(401).send({ error: 'Unauthorized', message: 'Invalid or missing token' });
    }
  });
}
