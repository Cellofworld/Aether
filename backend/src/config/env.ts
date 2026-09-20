import 'dotenv/config';

export const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  host: process.env.HOST || '0.0.0.0',
  databaseUrl: process.env.DATABASE_URL || 'postgresql://aether:aether@localhost:5432/aether',
  jwtSecret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
  mediaRoot: process.env.MEDIA_ROOT || '/media',
  transcodeRoot: process.env.TRANSCODE_ROOT || '/transcode',
  tmdbApiKey: process.env.TMDB_API_KEY || '',
  logLevel: process.env.LOG_LEVEL || 'info',
  corsOrigins: (process.env.CORS_ORIGINS || '*').split(','),
};
