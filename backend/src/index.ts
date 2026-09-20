import Fastify from 'fastify';
import { config } from './config/env';
import { buildApp } from './app';
import { prisma } from './config/database';
import bcrypt from 'bcrypt';

async function seedAdmin() {
  try {
    // Check if admin user already exists
    const existingAdmin = await prisma.user.findUnique({
      where: { email: 'admin@aether.local' },
    });

    if (existingAdmin) {
      console.log('✅ Admin user already exists');
      return;
    }

    // Create admin user
    const hashedPassword = await bcrypt.hash('admin123', 10);
    
    await prisma.user.create({
      data: {
        email: 'admin@aether.local',
        username: 'admin',
        password: hashedPassword,
        role: 'ADMIN',
      },
    });

    console.log('✅ Admin user created: admin@aether.local / admin123');

    // Create demo user
    const hashedUserPassword = await bcrypt.hash('user123', 10);
    
    await prisma.user.create({
      data: {
        email: 'user@aether.local',
        username: 'user',
        password: hashedUserPassword,
        role: 'USER',
      },
    });

    console.log('✅ Demo user created: user@aether.local / user123');
  } catch (error) {
    console.error('❌ Error seeding admin user:', error);
  }
}

async function start() {
  const fastify = Fastify({
    logger: {
      level: config.logLevel,
    },
  });
  
  await buildApp(fastify);
  
  try {
    // Connect to database
    await prisma.$connect();
    console.log('✅ Database connected');
    
    // Seed admin user
    await seedAdmin();
    
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
