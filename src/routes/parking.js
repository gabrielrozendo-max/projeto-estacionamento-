import { Router } from 'express';
import { createParkingController } from '../controllers/parking-controller.js';

export function createParkingRouter(database) {
  const router = Router();
  const controller = createParkingController(database);

  router.post('/entries', controller.registerEntry);
  router.post('/exits', controller.registerExit);

  return router;
}
