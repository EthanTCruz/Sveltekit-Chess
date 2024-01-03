<script type="module">
	
	import './GameplayStyles.css'
 
  import { Chess } from 'chess.js'
  import { boardT as importedBoardT } from '$lib/store';





  import { onMount } from 'svelte';


	/**
	 * @type {WebSocket}
	 */
	let ws;
	/**
	 * @type {string | null}
	 */
	let token;
	/**
	 * @type {string | null}
	 */
	let refresh_token;
	export let client_team = "w";
	export let turn = "0";
	let chess = new Chess()
	let winner = 'n'
	let showButtons = false;
	export let WinLossStatement = "";
	// Create a local copy of boardT
	let localBoardT = importedBoardT;
	
  onMount(() => {

	 token = localStorage.getItem('token');
	 refresh_token = localStorage.getItem('refresh_token');
	 ws = new WebSocket("ws://localhost:8000/ai/game");
    ws.onmessage = function(event) {
		try {

			var obj = JSON.parse(event.data);
			//console.log('Message from server:', event.data);

			console.log(obj)
			if ("access_token" in obj) { 
				localStorage.setItem('token', obj["access_token"]);
			  if ("refresh_token" in obj){
				localStorage.setItem('refresh_token', obj["refresh_token"]);
			  }
			}
			else{


			fen_components = obj["match"]
			client_team = obj["team"]
			turn = obj["turn"]
			winner = obj["winner"]
			setBoard(fen_components=fen_components)
			}
			// Work with the object
		  } catch (error) {
			console.error("Error parsing JSON:", event.data);
		  }


    };

	ws.onopen = () => {
		if (ws.readyState === WebSocket.OPEN) {
			console.log("WebSocket connection established");
  
			let message = {
				token: token,
				refresh_token: refresh_token
			};
			ws.send(JSON.stringify(message));

		} else {
			console.error('WebSocket is not open. ReadyState:', ws.readyState);
		}
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

  });
  
  // Function to flip the board
  function flipBoard() {

	localBoardT = localBoardT.reverse();

  }

  let fen_components = chess.fen()

  /**
	 * @param {string} fen_components
	 */


  function setBoard(fen_components){
	if (winner != 'n'){
		showButtons = true
		if (winner == 's'){
			console.log("Stalemate")
			WinLossStatement = "Stalemate";
		}
		else if (winner == client_team){
			console.log("Win")
			WinLossStatement = "Checkmate, you win!!!";

		}
		else {
			console.log("Lose")
			WinLossStatement = "Checkmate, you lose.";
		}
	}
	else{
		showButtons = false;
	}
	chess = new Chess(fen_components)

	const blacks = ['q','k','b','n','r','p']
	const whites = ['Q','K','B','N','R','P']
	let team
	let fen_board = fen_components.split(" ")[0].split("/")
	/*rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR*/

for (let i = 0; i < 8; i++){
	let board_column = 0
	for (let j = 0; j < fen_board[i].length; j++){
		let piece = fen_board[i].charAt(j)
		if (whites.includes(piece)){
			team = 'W'
			localBoardT[7-i][board_column] = `${piece}${team}`
			board_column++
		} else if(blacks.includes(piece)){
			team = 'B'
			localBoardT[7-i][board_column] = `${piece.toUpperCase()}${team}`
		board_column++
		} else {
			let value = Number(fen_board[i].charAt(j))
				for( let m = Number(board_column);m<Number(board_column+value);m++){
					localBoardT[7-i][m] = "  "
				}
				board_column += value
	}
}
}
if (client_team == 'w'){
	flipBoard()

}
  }

  let move_src = ""
	/**
	 * @param {number} row
	 * @param {number} column
	 */

function movePiece(column, row) {
if (turn != client_team){

	return(0) 
}

row++
if (client_team == 'w'){
	row = 9 - row
}
let moves = ['a','b','c','d','e','f','g','h']
let column_value = moves[column]
console.log(column_value,row)
let move = column_value+row

if (move_src == ""){
	move_src = move
} else {
try {
chess.move({from:move_src,to:move})
}
catch(error){
	console.log(`Invalid move: ${move_src}${move}`)
	move_src = ""
	return(0)
}
let full_move = move_src.concat(move)
if (token != null && ws.readyState === WebSocket.OPEN) {
	let message = {
		'token': token,
		'refresh_token': refresh_token,
		'move': full_move		
	};
	ws.send(JSON.stringify(message));
}

setBoard(fen_components=chess.fen())
move_src = ""
}

}

function PlayGame() {
	if (token != null && ws.readyState === WebSocket.OPEN) {
	let message = {
		token: token,
		refresh_token:refresh_token
	};
	ws.send(JSON.stringify(message));
}
  }



</script>


 {#if showButtons}
 <h1>{WinLossStatement}</h1>
 {:else}
 <h1>Your {client_team}, Turn is {turn}</h1>
 {/if} 
 {#if showButtons}
<button on:click={PlayGame}>Play Game</button>
{/if}

<div class="board">
	{#each localBoardT as row, rowIndex}
	  <div class="row">
		{#each row as cell, colIndex}
		  <!-- svelte-ignore a11y-click-events-have-key-events -->
		  <div class="cell" on:click="{() => movePiece(colIndex, rowIndex)}">
			{#if cell !== '  '}
            <img src={`/images/${cell}.png`} alt={cell}>
          {/if}

		  </div>
		{/each}
	  </div>
	{/each}
  </div>


