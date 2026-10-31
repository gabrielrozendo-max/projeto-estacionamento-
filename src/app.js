import express from 'express';
import { errorHandler } from './middleware/error-handler.js';
import { createParkingRouter } from './routes/parking.js';

export function createApp(database) {
  const app = express();

  app.disable('x-powered-by');
  app.use(express.json());
  app.use('/api/parking', createParkingRouter(database));
  app.use((request, response) => {
    response.status(404).json({
      error: {
        code: 'NOT_FOUND',
        message: 'O recurso pedido não existe.',
      },
    });
  });
  app.use(errorHandler);

  return app;
}
