import typing
import random

# Type hint for any object that has 'pnl' and 'max_drawdown' attributes for sorting
# Using Any or a Protocol would be better, but for simplicity assuming objects have these attrs.
T = typing.TypeVar('T')

def non_dominated_sorting(population: typing.Dict[int, T]) -> typing.List[typing.List[T]]:
    """
    Performs fast non-dominated sorting on a population.
    
    Args:
        population: Dictionary mapping IDs to individuals. Individuals must have 
                   'pnl', 'max_drawdown', 'dominates' (list), 'dominated_by' (int), 'rank' (int) attributes.
                   
    Returns:
        List of fronts (list of individuals).
    """
    fronts = []

    for id_1, indiv_1 in population.items():
        indiv_1.dominates = [] # Reset
        indiv_1.dominated_by = 0 # Reset
        
        for id_2, indiv_2 in population.items():
            # Check dominance: Minimize MaxDD, Maximize PnL
            # A dominates B if A.pnl >= B.pnl AND A.max_drawdown <= B.max_drawdown AND (one strict inequality)
            if indiv_1.pnl >= indiv_2.pnl and indiv_1.max_drawdown <= indiv_2.max_drawdown \
                    and (indiv_1.pnl > indiv_2.pnl or indiv_1.max_drawdown < indiv_2.max_drawdown):
                indiv_1.dominates.append(id_2)
            elif indiv_2.pnl >= indiv_1.pnl and indiv_2.max_drawdown <= indiv_1.max_drawdown \
                    and (indiv_2.pnl > indiv_1.pnl or indiv_2.max_drawdown < indiv_1.max_drawdown):
                indiv_1.dominated_by += 1

        if indiv_1.dominated_by == 0:
            if len(fronts) == 0:
                fronts.append([])
            fronts[0].append(indiv_1)
            indiv_1.rank = 0

    i = 0
    while True:
        if len(fronts) <= i:
            break
            
        next_front = []
        for indiv_1 in fronts[i]:
            for indiv_2_id in indiv_1.dominates:
                population[indiv_2_id].dominated_by -= 1
                if population[indiv_2_id].dominated_by == 0:
                    next_front.append(population[indiv_2_id])
                    population[indiv_2_id].rank = i + 1
        
        if len(next_front) > 0:
            fronts.append(next_front)
            i += 1
        else:
            break

    return fronts

def calculate_crowding_distance(population: typing.List[T]) -> typing.List[T]:
    """
    Calculates crowding distance for a list of individuals (usually a front).
    
    Args:
        population: List of individuals. Must have 'pnl', 'max_drawdown', 'crowding_distance' attributes.
    """
    if not population:
        return population

    length = len(population)
    for indiv in population:
        indiv.crowding_distance = 0

    for objective in ["pnl", "max_drawdown"]:
        # Sort by objective
        population = sorted(population, key=lambda x: getattr(x, objective))
        
        # Boundary points have infinite distance
        population[0].crowding_distance = float("inf")
        population[-1].crowding_distance = float("inf")

        min_val = getattr(population[0], objective)
        max_val = getattr(population[-1], objective)
        
        denom = max_val - min_val
        if denom == 0: 
            denom = 1 # Avoid div by zero

        for i in range(1, length - 1):
            distance = getattr(population[i + 1], objective) - getattr(population[i - 1], objective)
            population[i].crowding_distance += distance / denom

    return population

def select_by_tournament(population: typing.List[T], k: int = 2) -> T:
    """
    Selects the best individual from k random setup using crowded comparison operator.
    Prioritizes lower Rank, then higher Crowding Distance.
    """
    competitors = random.sample(population, k=k)
    
    # Sort key: (rank ASC, crowding_dist DESC)
    # We want MIN rank. If ranks equal, MAX crowding distance.
    # Python min/max logic:
    # If ranks differ: whoever has lower rank is better.
    # If ranks same: whoever has higher crowding is better.
    
    def comparison_key(indiv):
        return (indiv.rank, -indiv.crowding_distance)
        
    best = min(competitors, key=comparison_key)
    return best
