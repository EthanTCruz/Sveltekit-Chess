<script>
	import ChessGameplayComponent from '../../../components/ChessGameplayComponent.svelte';



	import { PUBLIC_MULTIPLAYER_CHESS_URL } from '$env/static/public';
  </script>
  
  <ChessGameplayComponent websocketUrl={PUBLIC_MULTIPLAYER_CHESS_URL} />