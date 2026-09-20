import fastifyJwt from '@fastify/jwt';

declare module 'fastify' {
  interface FastifyUser {
    id: string;
    email: string;
    username: string;
    role: 'ADMIN' | 'USER';
  }

  interface FastifyRequest {
    user: FastifyUser;
  }

  interface FastifyInstance {
    authenticate: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
    adminAuth: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
  }
}

declare module '@fastify/jwt' {
  interface FastifyJWT {
    payload: {
      id: string;
      email: string;
      username: string;
      role: 'ADMIN' | 'USER';
    };
    user: FastifyUser;
  }
}
