<script>
	import ChessGameplayComponent from '../../../components/ChessGameplayComponent.svelte';



	import { PUBLIC_COMPUTER_CHESS_URL } from '$env/static/public';
  </script>
  
  <ChessGameplayComponent websocketUrl={PUBLIC_COMPUTER_CHESS_URL} />