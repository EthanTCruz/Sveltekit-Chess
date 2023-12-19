// src/global.d.ts
import type { Locals as DefaultLocals } from '@sveltejs/kit';

declare global {
  namespace App {
    interface Locals extends DefaultLocals {
      session?: any; // Define the type of session as per your requirement
    }
  }
}
