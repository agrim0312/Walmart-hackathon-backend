# Vehicle Routing Problem (VRP) Solver 
# Project Overview
This application uses a Genetic Algorithm with the DEAP library to solve the Vehicle Routing Problem (VRP). It optimizes routes for a fleet of vehicles, aiming to minimize total travel distance and balance the workload across vehicles.
# Key Features
- Random Location Generation: Creates random coordinates for locations and a fixed depot.
- Genetic Algorithm: Optimizes routes for multiple vehicles based on distance and route balance.
- Fitness Evaluation: Calculates total travel distance and applies a balance penalty.
- Crossover & Mutation: Implements PMX crossover and shuffling mutation for route diversity.
- Selection Process: Uses tournament selection to evolve the best routes.
- Route Visualization: Plots routes for each vehicle with clear depot and location markers.
- Hall of Fame: Tracks and displays the best route configuration found.

# API Endpoints
- `POST /users`: Create a new user with hashed password and return an access token.
- `POST /token`: Authenticate user credentials and return an access token.
- `GET /users/me/`: Retrieve the currently authenticated user's details.
- `POST /get_routes`: Calculate and return optimal routes based on the provided location and vehicle details.
