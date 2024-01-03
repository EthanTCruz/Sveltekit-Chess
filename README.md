#Sveltekit Chess

##Description
My attempt at a full stack web application for multiplayer chess gameplay using Sveltekit and Fast API.


###Future Vision of Project
  - Add 'Play Computer' option to play against `https://github.com/EthanTCruz/chess_model` (after implementing MCST?)
  - Deploy in K8s

###How to Use:
  1. Open a terminal
  2. cd into project directory
  3. `pip install -r requirements.txt`
  4. cd into `backend`
  5. `uvicorn api.src.main:app --reload`
  6. Open a new terminal
  7. cd into `frontend`
  8. `npm run dev`
  9. Navigate to `http://localhost:5173/`
  10. Create an account and explore
    a. Once logged in click Play Game button
    b. Play Game is only for multiplayer use, so will have to create another account for use in a different browser account (user tokens are shared across profile) to test