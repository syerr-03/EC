
import streamlit as st
import pandas as pd
import random

# Page configuration
st.set_page_config(
    page_title="TV Scheduling using Genetic Algorithm",
    page_icon="📺",
    layout="wide"
)

# Title
st.title("📺 TV Scheduling using Genetic Algorithm")

st.write(
    "This application uses a Genetic Algorithm (GA) "
    "to optimize TV program scheduling based on audience ratings."
)

# Read the modified CSV dataset
df = pd.read_csv("program_ratings.csv")

# Convert CSV ratings into a dictionary
ratings = {
    row.iloc[0]: [float(value) for value in row.iloc[1:]]
    for _, row in df.iterrows()
}

# List of TV programs and time slots
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

# Fitness Function
def fitness_function(schedule):
    total_rating = 0

    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]

    return total_rating


# Initialize Population
def initialize_population(population_size):
    population = []

    for _ in range(population_size):
        schedule = [
            random.choice(all_programs)
            for _ in all_time_slots
        ]

        population.append(schedule)

    return population


# Selection Function (Tournament Selection)
def selection(population):
    tournament_size = 3

    candidates = random.sample(
        population,
        tournament_size
    )

    best_parent = max(
        candidates,
        key=fitness_function
    )

    return best_parent.copy()


# Crossover Function (Single-Point Crossover)
def crossover(parent1, parent2):
    crossover_point = random.randint(
        1, len(parent1) - 1
    )

    child1 = (
        parent1[:crossover_point]
        + parent2[crossover_point:]
    )

    child2 = (
        parent2[:crossover_point]
        + parent1[crossover_point:]
    )

    return child1, child2


# Mutation Function
def mutate(schedule):
    mutated_schedule = schedule.copy()

    mutation_point = random.randint(
        0, len(mutated_schedule) - 1
    )

    new_program = random.choice(all_programs)

    mutated_schedule[mutation_point] = new_program

    return mutated_schedule


# Genetic Algorithm Main Function
def genetic_algorithm(
    generations=100,
    population_size=50,
    crossover_rate=0.8,
    mutation_rate=0.2,
    elitism_size=2
):
    # Step 1: Initialize population
    population = initialize_population(population_size)

    # Step 2: Run generations
    for generation in range(generations):

        # Sort schedules based on fitness
        population.sort(
            key=fitness_function,
            reverse=True
        )

        # Step 3: Elitism - keep the best schedules
        new_population = [
            schedule.copy()
            for schedule in population[:elitism_size]
        ]

        # Step 4: Generate new schedules
        while len(new_population) < population_size:

            # Selection
            parent1 = selection(population)
            parent2 = selection(population)

            # Crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1 = parent1.copy()
                child2 = parent2.copy()

            # Mutation
            if random.random() < mutation_rate:
                child1 = mutate(child1)

            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        # Keep population size fixed
        population = new_population[:population_size]

    # Step 5: Find the best final schedule
    best_schedule = max(
        population,
        key=fitness_function
    )

    best_fitness = fitness_function(best_schedule)

    return best_schedule, best_fitness



st.subheader("📊 TV Program Ratings Dataset")
st.dataframe(df, use_container_width=True)

# Genetic Algorithm parameters
st.subheader("⚙️ Genetic Algorithm Parameters")

co_r = st.slider(
    "Crossover Rate (CO_R)",
    min_value=0.0,
    max_value=0.95,
    value=0.8,
    step=0.05
)

mut_r = st.slider(
    "Mutation Rate (MUT_R)",
    min_value=0.01,
    max_value=0.20,
    value=0.20,
    step=0.01
)

st.write("Selected Crossover Rate:", co_r)
st.write("Selected Mutation Rate:", mut_r)


# Run Genetic Algorithm when button is clicked
if st.button("Run Genetic Algorithm"):

    random.seed(42)

    with st.spinner("Running Genetic Algorithm..."):

        best_schedule, best_fitness = genetic_algorithm(
            generations=100,
            population_size=50,
            crossover_rate=co_r,
            mutation_rate=mut_r,
            elitism_size=2
        )

    st.success("Genetic Algorithm completed successfully!")

    # Display total ratings
    st.subheader("🏆 Best Schedule Result")
    st.metric("Total Ratings", f"{best_fitness:.2f}")

    # Convert schedule into a table
    schedule_df = pd.DataFrame({
        "Time Slot": [
            f"{hour:02d}:00"
            for hour in all_time_slots
        ],
        "TV Program": best_schedule,
        "Rating": [
            ratings[program][index]
            for index, program in enumerate(best_schedule)
        ]
    })

    # Display schedule table
    st.subheader("📺 Optimized TV Schedule")
    st.dataframe(
        schedule_df,
        use_container_width=True,
        hide_index=True,
        height=700
    )
