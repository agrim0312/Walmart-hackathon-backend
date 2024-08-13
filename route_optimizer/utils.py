import os
import random
import numpy as np
from passlib.context import CryptContext
import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import requests
from models import User  # Your user model
from database import get_db
from sqlalchemy.orm import Session
from deap import base, creator, tools, algorithms

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str):
    return pwd_context.hash(password)

def get_distance_matrix(locations):
    base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving"
    coordinates = ";".join([f"{loc[1]},{loc[0]}" for loc in locations])  # Format: longitude,latitude
    
    # Make the request to the Mapbox Matrix API
    response = requests.get(
            f"{base_url}/{coordinates}",
            params={
                "access_token": "pk.eyJ1IjoiYWdyaW0wMzEyIiwiYSI6ImNscW01eDYweDAyNWwya213cGR2Z2JyZmkifQ.VhMNA0js_M-_c9P3bMmqrw",
                "annotations": "distance"
            }
        )
    
    if response.status_code == 200:
        result = response.json()
        print(result)
        return result['distances']  # Matrix of distances in meters
    else:
        raise Exception(f"Error fetching data from Mapbox API: {response.text}")



def evalVRP(individual, num_vehicles, depot, locations, distance_matrix):
    total_distance = 0
    distances = []  # Track distance traveled by each vehicle for balance calculation
    num_locations = len(locations)
    
    # Function to get distance from distance_matrix
    def get_distance(loc1_index, loc2_index):
        return distance_matrix[loc1_index][loc2_index]

    # Ensure depot is the first location in locations
    locations = [depot] + locations

    # Calculate total distance for each vehicle's route
    for i in range(num_vehicles):
        route_indices = [0] + [individual[j] + 1 for j in range(i, len(individual), num_vehicles)] + [0]
        vehicle_distance = sum(get_distance(route_indices[k], route_indices[k + 1]) for k in range(len(route_indices) - 1))
        total_distance += vehicle_distance
        distances.append(vehicle_distance)
    
    balance_penalty = np.std(distances)  # Penalty for imbalance among vehicles
    return total_distance, balance_penalty

def create_evaluation_wrapper(num_vehicles, depot, locations, distance_matrix):
    def evalVRPWrapper(individual):
        return evalVRP(individual, num_vehicles, depot, locations, distance_matrix)
    return evalVRPWrapper

def setup_genetic_algorithm(num_locations,evalVRPWrapper):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  # Define fitness function to minimize. The two objectives are total distance and balance penalty.
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(num_locations), num_locations)  # Function to generate a list of unique, randomly ordered location indices
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)  # Function to create an individual as a shuffled list of location indices
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  # Function to create a population of individuals


    toolbox.register("evaluate", evalVRPWrapper)  # Register the evaluation function
    toolbox.register("mate", tools.cxPartialyMatched)  # Register the crossover function suitable for permutation-based representation
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)  # Register the mutation function to shuffle indices with a 5% chance per index
    toolbox.register("select", tools.selTournament, tournsize=3)  # Register the selection function using tournament selection

    return toolbox

def calculate_route(num_locations, num_vehicles, locations, depot):
    random.seed(42)  # Seed for reproducibility
    distance_matrix = get_distance_matrix([depot] + locations)
    evalVRPWrapper = create_evaluation_wrapper(num_vehicles, depot, locations, distance_matrix)
    toolbox = setup_genetic_algorithm(num_locations, evalVRPWrapper)
    pop = toolbox.population(n=300)  # Generate initial population
    hof = tools.HallOfFame(1)  # Hall of Fame to store the best individual

    # Setup statistics to track
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)

    # Run the genetic algorithm
    algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 300, stats=stats, halloffame=hof)

    # Plot the best route found
    return pop, stats, hof[0]