<script>
    import { goto } from '$app/navigation';
    let username = '';
    let password = '';
    let errorMessage = '';
  
    const handleLogin = async () => {
  try {
    const formData = new URLSearchParams();
formData.append('username', username);
formData.append('password', password);



    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    const data = await response.json();
    console.log('Registration successful', data);
    // You can store the token here
    if (data.access_token) { 
      localStorage.setItem('token', data.access_token);
    if (data.refresh_token){
      localStorage.setItem('refresh_token', data.refresh_token);
    }
// Replace loginSuccess with your actual success condition
      goto('/protected/homepage');
    }
  } catch (error) {
    if (error instanceof Error) {
        // Now we know it's an Error object and can safely access its properties
        errorMessage = error.message;
      } else {
        // Handle cases where the error is not an Error object
        errorMessage = 'An unknown error occurred';
      }
  }
};

    
  </script>
  
  <form on:submit|preventDefault={handleLogin}>
    <div>
      <label for="username">Username:</label>
      <input id="username" type="text" bind:value={username} />
    </div>
    <div>
      <label for="password">Password:</label>
      <input id="password" type="password" bind:value={password} />
    </div>
    <button type="submit">Register User</button>
    {#if errorMessage}
      <p style="color: red;">{errorMessage}</p>
    {/if}
  </form>
  