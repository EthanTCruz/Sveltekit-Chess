<script>
  import './HomepageStyles.css'
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
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token'); // Clear the token from localStorage
  goto('/login'); // Redirect to the login page
}

function playGame() { 
  goto('/protected/gameplay'); // Redirect to the login page
}
function playComputer() { 
  goto('/protected/computerGameplay'); // Redirect to the login page
}
  </script>
  <button on:click={logout}>Logout</button>
  <div>
    <!-- Your layout's HTML structure -->


    <slot />
    <button on:click={playGame}>Play Game</button>
    <button on:click={playComputer}>Play Computer</button>
    <!-- This is where the content of child pages will be rendered -->
  </div>