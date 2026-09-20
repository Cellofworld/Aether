import { FastifyInstance } from 'fastify';
import bcrypt from 'bcrypt';
import { prisma } from '../config/database';
import { z } from 'zod';

const registerSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(50),
  password: z.string().min(6),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

export async function authRoutes(fastify: FastifyInstance) {
  // Register
  fastify.post('/register', async (request, reply) => {
    try {
      const body = registerSchema.parse(request.body);
      
      const existingUser = await prisma.user.findFirst({
        where: {
          OR: [
            { email: body.email },
            { username: body.username },
          ],
        },
      });
      
      if (existingUser) {
        return reply.code(400).send({ 
          error: 'Bad Request', 
          message: 'User with this email or username already exists' 
        });
      }
      
      const hashedPassword = await bcrypt.hash(body.password, 10);
      
      const user = await prisma.user.create({
        data: {
          email: body.email,
          username: body.username,
          password: hashedPassword,
          role: 'USER',
        },
        select: {
          id: true,
          email: true,
          username: true,
          role: true,
        },
      });
      
      const token = fastify.jwt.sign({
        id: user.id,
        email: user.email,
        username: user.username,
        role: user.role,
      });
      
      reply.code(201).send({ user, token });
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({ 
          error: 'Validation Error', 
          details: error.errors 
        });
      }
      throw error;
    }
  });
  
  // Login
  fastify.post('/login', async (request, reply) => {
    try {
      const body = loginSchema.parse(request.body);
      
      const user = await prisma.user.findUnique({
        where: { email: body.email },
      });
      
      if (!user) {
        return reply.code(401).send({ 
          error: 'Unauthorized', 
          message: 'Invalid credentials' 
        });
      }
      
      const validPassword = await bcrypt.compare(body.password, user.password);
      
      if (!validPassword) {
        return reply.code(401).send({ 
          error: 'Unauthorized', 
          message: 'Invalid credentials' 
        });
      }
      
      const token = fastify.jwt.sign({
        id: user.id,
        email: user.email,
        username: user.username,
        role: user.role,
      });
      
      reply.send({ 
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          role: user.role,
        },
        token 
      });
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({ 
          error: 'Validation Error', 
          details: error.errors 
        });
      }
      throw error;
    }
  });
  
  // Get current user
  fastify.get('/me', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    const user = await prisma.user.findUnique({
      where: { id: request.user.id },
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
        createdAt: true,
      },
    });
    
    reply.send(user);
  });
}
