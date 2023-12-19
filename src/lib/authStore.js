import { writable } from 'svelte/store';

export const isAuthenticated = writable(false);


export function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
      // Optionally validate the token
      return true;
    }
    return false;
  }
  