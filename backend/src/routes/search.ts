import { FastifyInstance } from 'fastify';
import { prisma } from '../config/database';

export async function searchRoutes(fastify: FastifyInstance) {
  // Global search
  fastify.get('/', async (request, reply) => {
    const { q, type } = request.query as { q?: string; type?: string };
    
    if (!q || q.length < 2) {
      return reply.send({
        movies: [],
        series: [],
        episodes: [],
        people: [],
      });
    }
    
    const searchPattern = `%${q}%`;
    
    const [movies, series, episodes] = await Promise.all([
      // Search movies
      type === 'movie' || !type
        ? prisma.mediaItem.findMany({
            where: {
              type: 'MOVIE',
              status: 'READY',
              OR: [
                { title: { contains: searchPattern, mode: 'insensitive' } },
                { originalTitle: { contains: searchPattern, mode: 'insensitive' } },
              ],
            },
            take: 10,
            include: {
              movie: true,
              videoFiles: {
                take: 1,
                select: { width: true, height: true, hdr: true },
              },
            },
          })
        : [],
      
      // Search series
      type === 'series' || !type
        ? prisma.mediaItem.findMany({
            where: {
              type: 'SERIES',
              status: 'READY',
              OR: [
                { title: { contains: searchPattern, mode: 'insensitive' } },
                { originalTitle: { contains: searchPattern, mode: 'insensitive' } },
              ],
            },
            take: 10,
            include: {
              series: true,
              videoFiles: {
                take: 1,
                select: { width: true, height: true, hdr: true },
              },
            },
          })
        : [],
      
      // Search episodes
      type === 'episode' || !type
        ? prisma.episode.findMany({
            where: {
              title: { contains: searchPattern, mode: 'insensitive' },
            },
            take: 10,
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
          })
        : [],
    ]);
    
    reply.send({
      movies,
      series,
      episodes,
    });
  });
}
