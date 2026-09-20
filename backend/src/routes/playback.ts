import { FastifyInstance } from 'fastify';
import { prisma } from '../config/database';
import { z } from 'zod';

const playbackProgressSchema = z.object({
  mediaItemId: z.string().optional(),
  episodeId: z.string().optional(),
  position: z.number().int().positive(),
  duration: z.number().int().positive(),
});

export async function playbackRoutes(fastify: FastifyInstance) {
  // Update playback progress
  fastify.post('/progress', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    try {
      const body = playbackProgressSchema.parse(request.body);
      const userId = request.user.id;
      
      const { mediaItemId, episodeId, position, duration } = body;
      
      const watched = position >= duration * 0.9; // 90% threshold
      
      // Upsert watch progress
      const whereClause: { userId: string; mediaItemId?: string; episodeId?: string } = {
        userId,
      };
      
      if (mediaItemId) {
        whereClause.mediaItemId = mediaItemId;
      }
      if (episodeId) {
        whereClause.episodeId = episodeId;
      }

      const progress = await prisma.watchProgress.upsert({
        where: whereClause as any,
        update: {
          position,
          duration,
          watched,
          lastWatched: new Date(),
        },
        create: {
          userId,
          mediaItemId: mediaItemId || undefined,
          episodeId: episodeId || undefined,
          position,
          duration,
          watched,
        },
      });
      
      // Create or update watch history
      if (episodeId) {
        const episode = await prisma.episode.findUnique({
          where: { id: episodeId },
          include: { season: { include: { series: true } } },
        });
        
        if (episode) {
          await prisma.watchHistory.upsert({
            where: {
              userId_episodeId: {
                userId,
                episodeId,
              },
            },
            update: {
              endedAt: watched ? new Date() : null,
              playCount: { increment: watched ? 1 : 0 },
            },
            create: {
              userId,
              episodeId,
              startedAt: new Date(),
              endedAt: watched ? new Date() : null,
            },
          });
        }
      } else if (mediaItemId) {
        await prisma.watchHistory.upsert({
          where: {
            userId_mediaItemId: {
              userId,
              mediaItemId,
            },
          },
          update: {
            endedAt: watched ? new Date() : null,
            playCount: { increment: watched ? 1 : 0 },
          },
          create: {
            userId,
            mediaItemId,
            startedAt: new Date(),
            endedAt: watched ? new Date() : null,
          },
        });
      }
      
      reply.send(progress);
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
  
  // Get continue watching
  fastify.get('/continue-watching', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    const userId = request.user.id;
    
    const progress = await prisma.watchProgress.findMany({
      where: {
        userId,
        watched: false,
        position: { gt: 30 }, // More than 30 seconds watched
      },
      orderBy: { lastWatched: 'desc' },
      take: 20,
      include: {
        mediaItem: {
          include: {
            movie: true,
            series: true,
            videoFiles: {
              take: 1,
              select: { width: true, height: true },
            },
          },
        },
        episode: {
          include: {
            season: {
              include: {
                series: {
                  include: {
                    mediaItem: true,
                  },
                },
              },
            },
          },
        },
      },
    });
    
    reply.send(progress);
  });
  
  // Get watch history
  fastify.get('/history', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    const { page = '1', limit = '20' } = request.query as { page?: string; limit?: string };
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const [history, total] = await Promise.all([
      prisma.watchHistory.findMany({
        where: { userId: request.user.id },
        skip,
        take: parseInt(limit),
        orderBy: { startedAt: 'desc' },
        include: {
          mediaItem: {
            include: {
              movie: true,
              series: true,
            },
          },
          episode: {
            include: {
              season: {
                include: {
                  series: {
                    include: {
                      mediaItem: true,
                    },
                  },
                },
              },
            },
          },
        },
      }),
      prisma.watchHistory.count({
        where: { userId: request.user.id },
      }),
    ]);
    
    reply.send({
      items: history,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / parseInt(limit)),
      },
    });
  });
  
  // Toggle watchlist
  fastify.post('/watchlist/:mediaItemId', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    const { mediaItemId } = request.params as { mediaItemId: string };
    const userId = request.user.id;
    
    const existing = await prisma.watchlist.findUnique({
      where: {
        userId_mediaItemId: {
          userId,
          mediaItemId,
        },
      },
    });
    
    if (existing) {
      await prisma.watchlist.delete({
        where: { id: existing.id },
      });
      reply.send({ added: false });
    } else {
      await prisma.watchlist.create({
        data: {
          userId,
          mediaItemId,
        },
      });
      reply.send({ added: true });
    }
  });
  
  // Get watchlist
  fastify.get('/watchlist', { 
    preHandler: [fastify.authenticate] 
  }, async (request, reply) => {
    const watchlist = await prisma.watchlist.findMany({
      where: { userId: request.user.id },
      orderBy: { createdAt: 'desc' },
      include: {
        mediaItem: {
          include: {
            movie: true,
            series: true,
            videoFiles: {
              take: 1,
              select: { width: true, height: true, hdr: true },
            },
          },
        },
      },
    });
    
    reply.send(watchlist);
  });
}
