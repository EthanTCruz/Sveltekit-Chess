<script type="module">
 
  import { Chess } from 'chess.js'
  import {board, boardT} from '$lib/store'
  import { onMount } from 'svelte';

	/**
	 * @type {WebSocket}
	 */
	let ws;
	/**
	 * @type {string | null}
	 */
	let token;

  onMount(() => {
	console.log(1)
	 token = localStorage.getItem('token');
	 ws = new WebSocket("ws://localhost:8000/ws/game");
    ws.onmessage = function(event) {
		
		console.log('Message from server:', event.data);

    };

	ws.onopen = () => {
		console.log("WebSocket connection established");
  
		// Send a message once the connection is open

		let chess = new Chess()
		let fen_components = chess.fen()
		setBoard(fen_components=fen_components);
	  };

  
	  ws.onmessage = event => {
		console.log(event.data);
	  };
  
	  ws.onerror = error => {
		console.error('WebSocket error:', error);
	  };
  
	  ws.onclose = () => {
		console.log("WebSocket connection closed");
	  };
	  /**
	   * @param {string | ArrayBufferLike | Blob | ArrayBufferView} message
	   */
	   function sendMessage(message){
		console.log(ws.readyState)
		ws.send(message)
	  }
  });
  

   let chess = new Chess()
  let fen_components = chess.fen()

  /**
	 * @param {string} fen_components
	 */


  function setBoard(fen_components){
	const blacks = ['q','k','b','n','r','p']
	const whites = ['Q','K','B','N','R','P']
	let team
	let fen_board = fen_components.split(" ")[0].split("/")
	/*rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR*/

	

	if (token != null){
		ws.send(token);
	}



for (let i = 0; i < 8; i++){
	let board_column = 0
	for (let j = 0; j < fen_board[i].length; j++){
		let piece = fen_board[i].charAt(j)
		if (whites.includes(piece)){
			team = 'W'
			boardT[7-i][board_column] = `${piece}${team}`
			board_column++
		} else if(blacks.includes(piece)){
			team = 'B'
			boardT[7-i][board_column] = `${piece.toUpperCase()}${team}`
		board_column++
		} else {
			let value = Number(fen_board[i].charAt(j))
				for( let m = Number(board_column);m<Number(board_column+value);m++){
					boardT[7-i][m] = "  "
				}
				board_column += value
	}
}
}
  }

  let move_src = ""
	/**
	 * @param {number} row
	 * @param {number} column
	 */

function movePiece(column, row) {

row++
let moves = ['a','b','c','d','e','f','g','h']
let column_value = moves[column]
console.log(column_value,row)
let move = column_value+row
if (move_src == ""){
	move_src = move
} else {
chess.move({from:move_src,to:move})
setBoard(fen_components=chess.fen())
move_src = ""
}

}



</script>


  

<div class="board">
	{#each boardT as row, rowIndex}
	  <div class="row">
		{#each row as cell, colIndex}
		  <!-- svelte-ignore a11y-click-events-have-key-events -->
		  <div class="cell" on:click="{() => movePiece(colIndex, rowIndex)}">
			{cell}
		  </div>
		{/each}
	  </div>
	{/each}
  </div>

<style>

/* Add styles to center the board within its container */
.board {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: auto;
  height: 100vh; /* Full height of the viewport */
}

.row {
  display: flex;
  justify-content: center;

}

.cell {
  width: 60px; /* Adjusted for better visibility */
  height: 60px; /* Adjusted for better visibility */
  text-align: center;
  padding: 10px; /* Adjust padding as needed */
  border: 3px solid black;
}

</style>
