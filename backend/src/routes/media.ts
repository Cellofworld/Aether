import { FastifyInstance } from 'fastify';
import { prisma } from '../config/database';

export async function mediaRoutes(fastify: FastifyInstance) {
  // Get movies
  fastify.get('/movies', async (request, reply) => {
    const { page = '1', limit = '20' } = request.query as { page?: string; limit?: string };
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const [movies, total] = await Promise.all([
      prisma.mediaItem.findMany({
        where: { type: 'MOVIE', status: 'READY' },
        skip,
        take: parseInt(limit),
        orderBy: { releaseDate: 'desc' },
        include: {
          movie: true,
          videoFiles: {
            take: 1,
            select: { width: true, height: true, hdr: true, codec: true },
          },
          watchProgress: {
            where: { userId: request.user?.id || '' },
            take: 1,
          },
        },
      }),
      prisma.mediaItem.count({ where: { type: 'MOVIE', status: 'READY' } }),
    ]);
    
    reply.send({
      items: movies,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / parseInt(limit)),
      },
    });
  });
  
  // Get single movie
  fastify.get('/movies/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    
    const movie = await prisma.mediaItem.findFirst({
      where: { id, type: 'MOVIE' },
      include: {
        movie: true,
        videoFiles: {
          include: {
            audioTracks: true,
            subtitleTracks: true,
          },
        },
        watchProgress: {
          where: { userId: request.user?.id || '' },
          take: 1,
        },
        watchlist: {
          where: { userId: request.user?.id || '' },
          take: 1,
        },
      },
    });
    
    if (!movie) {
      return reply.code(404).send({ error: 'Not Found', message: 'Movie not found' });
    }
    
    reply.send(movie);
  });
  
  // Get series
  fastify.get('/series', async (request, reply) => {
    const { page = '1', limit = '20' } = request.query as { page?: string; limit?: string };
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const [series, total] = await Promise.all([
      prisma.mediaItem.findMany({
        where: { type: 'SERIES', status: 'READY' },
        skip,
        take: parseInt(limit),
        orderBy: { releaseDate: 'desc' },
        include: {
          series: {
            include: {
              seasons: {
                orderBy: { seasonNumber: 'asc' },
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
      prisma.mediaItem.count({ where: { type: 'SERIES', status: 'READY' } }),
    ]);
    
    reply.send({
      items: series,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / parseInt(limit)),
      },
    });
  });
  
  // Get single series
  fastify.get('/series/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    
    const series = await prisma.mediaItem.findFirst({
      where: { id, type: 'SERIES' },
      include: {
        series: {
          include: {
            seasons: {
              orderBy: { seasonNumber: 'asc' },
              include: {
                episodes: {
                  orderBy: { episodeNumber: 'asc' },
                  include: {
                    videoFiles: {
                      take: 1,
                      include: {
                        audioTracks: true,
                        subtitleTracks: true,
                      },
                    },
                    watchProgress: {
                      where: { userId: request.user?.id || '' },
                      take: 1,
                    },
                  },
                },
              },
            },
          },
        },
        watchlist: {
          where: { userId: request.user?.id || '' },
          take: 1,
        },
      },
    });
    
    if (!series) {
      return reply.code(404).send({ error: 'Not Found', message: 'Series not found' });
    }
    
    reply.send(series);
  });
  
  // Get episode details
  fastify.get('/episodes/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    
    const episode = await prisma.episode.findUnique({
      where: { id },
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
        videoFiles: {
          include: {
            audioTracks: true,
            subtitleTracks: true,
          },
        },
        watchProgress: {
          where: { userId: request.user?.id || '' },
          take: 1,
        },
      },
    });
    
    if (!episode) {
      return reply.code(404).send({ error: 'Not Found', message: 'Episode not found' });
    }
    
    reply.send(episode);
  });
}
