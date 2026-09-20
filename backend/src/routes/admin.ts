import { FastifyInstance } from 'fastify';
import { prisma } from '../config/database';

export async function adminRoutes(fastify: FastifyInstance) {
  // Dashboard stats
  fastify.get('/dashboard', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const [
      movieCount,
      seriesCount,
      episodeCount,
      userCount,
      libraryCount,
      activeScanJobs,
    ] = await Promise.all([
      prisma.mediaItem.count({ where: { type: 'MOVIE' } }),
      prisma.mediaItem.count({ where: { type: 'SERIES' } }),
      prisma.episode.count(),
      prisma.user.count(),
      prisma.library.count(),
      prisma.scanJob.count({ where: { status: 'RUNNING' } }),
    ]);
    
    // Get storage info (simplified - in production use fs.stats)
    const storageUsed = 0; // Would need filesystem access
    
    reply.send({
      stats: {
        movies: movieCount,
        series: seriesCount,
        episodes: episodeCount,
        users: userCount,
        libraries: libraryCount,
        activeStreams: 0, // Would need session tracking
        transcodingSessions: 0,
        storageUsed,
      },
      activeScans: activeScanJobs,
    });
  });
  
  // Get all scan jobs
  fastify.get('/jobs', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const jobs = await prisma.scanJob.findMany({
      orderBy: { startedAt: 'desc' },
      take: 50,
      include: {
        library: true,
      },
    });
    
    reply.send(jobs);
  });
  
  // Start library scan
  fastify.post('/scan/:libraryId', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { libraryId } = request.params as { libraryId: string };
    
    // Check if library exists
    const library = await prisma.library.findUnique({
      where: { id: libraryId },
    });
    
    if (!library) {
      return reply.code(404).send({ error: 'Not Found', message: 'Library not found' });
    }
    
    // Check for existing running job for this library
    const existingJob = await prisma.scanJob.findFirst({
      where: {
        libraryId,
        status: 'RUNNING',
      },
    });
    
    if (existingJob) {
      return reply.code(400).send({ 
        error: 'Bad Request', 
        message: 'Scan already in progress for this library',
        jobId: existingJob.id,
      });
    }
    
    // Create scan job
    const job = await prisma.scanJob.create({
      data: {
        libraryId,
        status: 'PENDING',
      },
    });
    
    // In a real implementation, this would trigger a background worker
    // For now, we'll just return the job ID
    // The actual scanning would be done by a separate process/worker
    
    reply.code(202).send({
      message: 'Scan job created',
      job,
    });
  });
  
  // Get scan job status
  fastify.get('/jobs/:id', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    
    const job = await prisma.scanJob.findUnique({
      where: { id },
      include: {
        library: true,
      },
    });
    
    if (!job) {
      return reply.code(404).send({ error: 'Not Found', message: 'Job not found' });
    }
    
    reply.send(job);
  });
  
  // Get all users
  fastify.get('/users', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const users = await prisma.user.findMany({
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    });
    
    reply.send(users);
  });
  
  // Update user role
  fastify.put('/users/:id/role', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    const { role } = request.body as { role: 'ADMIN' | 'USER' };
    
    if (!['ADMIN', 'USER'].includes(role)) {
      return reply.code(400).send({ error: 'Bad Request', message: 'Invalid role' });
    }
    
    const user = await prisma.user.update({
      where: { id },
      data: { role },
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
      },
    });
    
    reply.send(user);
  });
  
  // Delete user
  fastify.delete('/users/:id', { 
    preHandler: [fastify.adminAuth] 
  }, async (request, reply) => {
    const { id } = request.params as { id: string };
    
    // Prevent deleting yourself
    if (id === request.user.id) {
      return reply.code(400).send({ 
        error: 'Bad Request', 
        message: 'Cannot delete your own account' 
      });
    }
    
    await prisma.user.delete({
      where: { id },
    });
    
    reply.code(204).send();
  });
}
