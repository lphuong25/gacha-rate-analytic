import random
import numpy as np

# df = pd.read_excel('gachagame.xlsx')

# calculate probability to get an ssr on a certain budget
def calc_probability(row, total_pulls):
    base_rate = row['Base_rate']
    soft_pity = row['Soft_pity']
    soft_pity_increment = row['Soft_rate']
    hard_pity = row['Hard_pity']

    chance_of_losing_all = 1.0

    for pull in range(1, total_pulls + 1):
        current_rate = base_rate

        # soft pity system if available
        if soft_pity > 0 and pull > soft_pity:
            current_rate += soft_pity_increment * (pull - soft_pity) 

        # hard pity 
        if hard_pity > 0 and pull >= hard_pity:
            current_rate = 1.0

        # ensure rate bound between 0 and 1
        current_rate = min(max(current_rate, 0.0), 1.0)
        chance_of_losing_all *= (1 - current_rate)

    probability = (1 - chance_of_losing_all) * 100
    return round(probability, 2)

# generate a curve for total pulls
def generate_probability_curve(row, max_pulls = 300, step = 10):
    pulls_range = []
    probabilities = []

    for pulls in range(0, max_pulls + step, step):
        prob = calc_probability(row, pulls)
        pulls_range.append(pulls)
        probabilities.append(prob)

    return pulls_range, probabilities

# Monte Carlo model to calculate the first ssr pull
def first_ssr_pull(row):

    pull = 0

    while True:
        pull += 1
        rate = row["Base_rate"]

        if (row["Soft_pity"] > 0 and pull > row["Soft_pity"]):
            rate += (row["Soft_rate"] * (pull - row["Soft_pity"]))
        
        rate = min(rate, 1.0)

        if (row["Hard_pity"] > 0 and pull >= row["Hard_pity"]):
            rate = 1.0
        
        rate = min(max(rate, 0.0), 1)
        
        if random.random() < rate:
            return pull

# run simulation
def monte_carlo(row, simulations = 10000):
    results = [first_ssr_pull(row) for _ in range(simulations)]

    return {
        "mean": np.mean(results),
        "median": np.median(results),
        "std": np.std(results),
        "results": results
    }

