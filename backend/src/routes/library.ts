import { FastifyInstance } from 'fastify';
import { prisma } from '../config/database';
import { z } from 'zod';

const createLibrarySchema = z.object({
  name: z.string().min(1).max(100),
  type: z.enum(['MOVIES', 'SERIES', 'ANIME', 'CARTOONS', 'DOCUMENTARIES', 'MUSIC', 'PHOTOS']),
  paths: z.array(z.string()).min(1),
});

export async function libraryRoutes(fastify: FastifyInstance) {
  // Get all libraries
  fastify.get('/', async (request, reply) => {
    const libraries = await prisma.library.findMany({
      include: {
        _count: {
          select: { mediaItems: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
    
    reply.send(libraries);
  });
  
  // Get single library
  fastify.get('/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    
    const library = await prisma.library.findUnique({
      where: { id },
      include: {
        mediaItems: {
          take: 50,
          orderBy: { createdAt: 'desc' },
          include: {
            movie: true,
            series: {
              include: {
                seasons: {
                  include: {
                    episodes: {
                      take: 5,
                    },
                  },
                },
              },
            },
            videoFiles: {
              take: 1,
            },
          },
        },
      },
    });
    
    if (!library) {
      return reply.code(404).send({ error: 'Not Found', message: 'Library not found' });
    }
    
    reply.send(library);
  });
  
  // Create library (admin only)
  fastify.post('/', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    try {
      const body = createLibrarySchema.parse(request.body);
      
      const library = await prisma.library.create({
        data: body,
      });
      
      reply.code(201).send(library);
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
  
  // Update library (admin only)
  fastify.put('/:id', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const { name, type, paths } = request.body as any;
    
    const library = await prisma.library.update({
      where: { id },
      data: { name, type, paths },
    });
    
    reply.send(library);
  });
  
  // Delete library (admin only)
  fastify.delete('/:id', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    
    await prisma.library.delete({
      where: { id },
    });
    
    reply.code(204).send();
  });
  
  // Get library items
  fastify.get('/:id/items', async (request, reply) => {
    const { id } = request.params as { id: string };
    const { page = '1', limit = '20', type } = request.query as { page?: string; limit?: string; type?: string };
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const where: any = { libraryId: id };
    if (type) {
      where.type = type;
    }
    
    const [items, total] = await Promise.all([
      prisma.mediaItem.findMany({
        where,
        skip,
        take: parseInt(limit),
        orderBy: { createdAt: 'desc' },
        include: {
          movie: true,
          series: {
            include: {
              seasons: {
                include: {
                  _count: { select: { episodes: true } },
                },
              },
            },
          },
          videoFiles: {
            take: 1,
            select: { width: true, height: true, hdr: true },
          },
          watchProgress: {
            where: { userId: request.user?.id || '' },
            take: 1,
          },
        },
      }),
      prisma.mediaItem.count({ where }),
    ]);
    
    reply.send({
      items,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / parseInt(limit)),
      },
    });
  });
}
