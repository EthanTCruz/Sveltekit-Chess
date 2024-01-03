<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
  
    onMount(() => {
      const token = localStorage.getItem('token');
      if (!token) {
        goto('/login');
      }
      // You can add more client-side logic here if needed
    });


function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token'); // Clear the token from localStorage
  goto('/login'); // Redirect to the login page
}
function home() {
  goto('/protected/homepage'); // Redirect to the login page
}
  </script>
  <button on:click={logout}>Logout</button>
  <button on:click={home}>Home</button>
  <div>
    <!-- Your layout's HTML structure -->
  
    <slot />
    <!-- This is where the content of child pages will be rendered -->
  </div>