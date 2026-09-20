import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');
  
  // Create admin user
  const hashedPassword = await bcrypt.hash('admin123', 10);
  
  const admin = await prisma.user.upsert({
    where: { email: 'admin@aether.local' },
    update: {},
    create: {
      email: 'admin@aether.local',
      username: 'admin',
      password: hashedPassword,
      role: 'ADMIN',
    },
  });
  
  console.log(`✅ Created admin user: ${admin.username}`);
  
  // Create demo user
  const userPassword = await bcrypt.hash('user123', 10);
  
  const user = await prisma.user.upsert({
    where: { email: 'user@aether.local' },
    update: {},
    create: {
      email: 'user@aether.local',
      username: 'user',
      password: userPassword,
      role: 'USER',
    },
  });
  
  console.log(`✅ Created user: ${user.username}`);
  
  console.log('🎉 Seeding completed!');
  console.log('');
  console.log('Login credentials:');
  console.log('  Admin: admin@aether.local / admin123');
  console.log('  User:  user@aether.local / user123');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
