<script>
    export let show = false;
    export let title = '';
    /**
	 * @type {(arg0: string) => void}
	 */
     export let onSelect;
  
    /**
	 * @param {string} choice
	 */
    function handleSelect(choice) {
        onSelect(choice);
    }
  </script>
  
  {#if show}
    <div class="popup">
      <div class="popup-content">
        <h2>{title}</h2>
        <button on:click={() => handleSelect('n')}>Knight</button>
        <button on:click={() => handleSelect('q')}>Queen</button>
        <button on:click={() => handleSelect('r')}>Rook</button>
        <button on:click={() => handleSelect('b')}>Bishop</button>
      </div>
    </div>
  {/if}
  
  <style>
    .popup {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
    }
  
    .popup-content {
      background: white;
      padding: 20px;
      border-radius: 5px;
      text-align: center;
    }
  
    button {
      margin: 5px;
      padding: 10px 20px;
    }
  </style>
  