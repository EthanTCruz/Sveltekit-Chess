// src/hooks.server.js or src/hooks.ts
export async function handle({ event, resolve }) {
    const session = {} // Your logic to get session data
  
    event.locals.session = session; // Attach session data to event.locals
  
    return await resolve(event);
  }
  