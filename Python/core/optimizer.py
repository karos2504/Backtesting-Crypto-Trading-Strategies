import random
import typing
import copy

from common.utils import resample_timeframe
from services.database import Hdf5Client
from models.result import BacktestResult
from core.genetic_utils import non_dominated_sorting, calculate_crowding_distance, select_by_tournament

from strategies.obv import ObvStrategy
from strategies.ichimoku import IchimokuStrategy
from strategies.support_resistance import SupResStrategy
from strategies.sma import SmaStrategy
from strategies.psar import PsarStrategy

class Nsga2:
    def __init__(self, exchange: str, symbol: str, strategy: str, tf: str, from_time: int, to_time: int,
                 population_size: int):
        self.exchange = exchange
        self.symbol = symbol
        self.tf = tf
        self.from_time = from_time
        self.to_time = to_time
        self.population_size = population_size

        self.strategy_map = {
            'obv': ObvStrategy,
            'ichimoku': IchimokuStrategy,
            'support_resistance': SupResStrategy,
            'sma': SmaStrategy, 
            'psar': PsarStrategy 
        }

        if strategy not in self.strategy_map:
             raise ValueError(f"Strategy {strategy} not implemented.")
        
        self.strategy_instance = self.strategy_map[strategy]()
        self.params_data = self.strategy_instance.params
        self.population_params = []

        # Load data
        h5_db = Hdf5Client(exchange)
        self.data = h5_db.get_data(symbol, from_time, to_time)
        self.data = resample_timeframe(self.data, tf)


    def create_initial_population(self) -> typing.List[BacktestResult]:
        population = []
        while len(population) < self.population_size:
            backtest = BacktestResult()
            for p_code, p in self.params_data.items():
                if p["type"] == int:
                    backtest.parameters[p_code] = random.randint(p["min"], p["max"])
                elif p["type"] == float:
                    backtest.parameters[p_code] = round(random.uniform(p["min"], p["max"]), p.get("decimal", 2))

            backtest.parameters = self.strategy_instance.validate_params(backtest.parameters)

            if backtest not in population:
                population.append(backtest)
                self.population_params.append(backtest.parameters)

        return population

    def create_new_population(self, fronts: typing.List[typing.List[BacktestResult]]) -> typing.List[BacktestResult]:
        new_pop = []
        for front in fronts:
            if len(new_pop) + len(front) > self.population_size:
                max_individuals = self.population_size - len(new_pop)
                if max_individuals > 0:
                    # Sort by crowding distance (descending)
                    new_pop += sorted(front, key=lambda x: getattr(x, "crowding_distance"), reverse=True)[:max_individuals]
            else:
                new_pop += front
        return new_pop

    def create_offspring_population(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        offspring_pop = []
        
        while len(offspring_pop) != self.population_size:
            parents = [select_by_tournament(population) for _ in range(2)]

            new_child = BacktestResult()
            new_child.parameters = copy.copy(parents[0].parameters)

            # Crossover
            number_of_crossovers = random.randint(1, len(self.params_data))
            params_to_cross = random.sample(list(self.params_data.keys()), k=number_of_crossovers)

            for p in params_to_cross:
                new_child.parameters[p] = copy.copy(parents[1].parameters[p])

            # Mutation
            number_of_mutations = random.randint(0, len(self.params_data))
            params_to_change = random.sample(list(self.params_data.keys()), k=number_of_mutations)

            for p in params_to_change:
                mutations_strength = random.uniform(-2, 2)
                val = new_child.parameters[p] * (1 + mutations_strength)
                p_config = self.params_data[p]
                
                # Cast and Clip
                val = p_config["type"](max(p_config["min"], min(val, p_config["max"])))
                
                if p_config["type"] == float:
                    val = round(val, p_config.get("decimal", 2))
                    
                new_child.parameters[p] = val

            # Constraints Check
            new_child.parameters = self.strategy_instance.validate_params(new_child.parameters)

            if new_child.parameters not in self.population_params:
                offspring_pop.append(new_child)
                self.population_params.append(new_child.parameters)

        return offspring_pop

    def evaluate_population(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        for bt in population:
            bt.pnl, bt.max_drawdown = self.strategy_instance.backtest(self.data, **bt.parameters)
            # Penalize invalid results
            if bt.pnl == 0 and bt.max_drawdown == 0:
                 # Assign worst possible fitness to filter out
                bt.pnl = -float("inf")
                bt.max_drawdown = float("inf")
        return population

    def run(self, generations: int, mutation_rate: float) -> typing.List[BacktestResult]:
        # Initial Population
        population = self.create_initial_population()
        population = self.evaluate_population(population)
        
        # Initial Sorting
        fronts = non_dominated_sorting({i: p for i, p in enumerate(population)})
        for front in fronts:
            calculate_crowding_distance(front)
        
        parents = population # Initial parents are the first population

        for gen in range(generations):
            # Create offspring
            offspring = self.create_offspring_population(parents)
            offspring = self.evaluate_population(offspring)
            
            # Combine
            combined_pop = parents + offspring
            
            # Sort combined
            fronts = non_dominated_sorting({i: p for i, p in enumerate(combined_pop)})
            for front in fronts:
                calculate_crowding_distance(front)
            
            # Select next generation
            parents = self.create_new_population(fronts)
            
            print(f"Generation {gen+1}/{generations} complete. Best PnL: {max(p.pnl for p in parents) if parents else 0}")
            
        return parents
        