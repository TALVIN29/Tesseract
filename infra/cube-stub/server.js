/**
 * Sprint 0 stub server — Inner Cube placeholder.
 * Exists solely to satisfy Docker Compose healthcheck during environment bootstrap.
 * REPLACED entirely in Sprint 1 by the Fastify application (TESS-015).
 * Do not add logic here.
 */
const http = require('http');

const PORT = process.env.CUBE_PORT || 3100;

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'ok',
      note: 'Sprint 0 infrastructure stub — not the real Cube API',
      db: 'not_connected',
      redis: 'not_connected'
    }));
    return;
  }

  res.writeHead(501);
  res.end(JSON.stringify({
    error: 'Not Implemented',
    note: 'Sprint 0 stub. Full Cube API implemented in Sprint 1 (TESS-015 through TESS-037).'
  }));
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[TESSERACT STUB] Cube API stub listening on port ${PORT}`);
  console.log('[TESSERACT STUB] Replace this in Sprint 1 with the Fastify application.');
});
