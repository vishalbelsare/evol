from evol import Individual, Evolution
from copy import deepcopy
from random import choices


class Population:

    def __init__(self, init_function, eval_function, size=100, maximize=True):
        self.eval_function = eval_function
        self.generation = 0
        self.individuals = [Individual(init_function=init_function) for _ in range(size)]
        self.intended_size = size
        self.maximize = maximize

    def __iter__(self):
        return self.individuals.__iter__()

    def __getitem__(self, i):
        return self.individuals[i]

    def __len__(self):
        return len(self.individuals)

    def __repr__(self):
        return f"<Population object with size {len(self)}>"

    def evolve(self, evolution: Evolution):
        result = deepcopy(self)
        for step in evolution:
            step.apply(result)
        return result

    def evaluate(self, lazy: bool=False) -> 'Population':
        """Evaluate the individuals in the population
        
        :param lazy: If True, do not evaluate already evaluated individuals. Defaults to False.
        :type lazy: bool
        :return: Population
        """
        for individual in self.individuals:
            individual.evaluate(eval_function=self.eval_function, lazy=lazy)
        return self  # do we want to copy here?

    def apply(self, func, **kwargs) -> 'Population':
        """apply(f(Population, **kwargs) -> Population, **kwargs)"""
        return func(self, **kwargs)

    def map(self, func, **kwargs) -> 'Population':
        """map(f(Individual, **kwargs) -> Individual, **kwargs)"""
        self.individuals = [func(individual, **kwargs) for individual in self.individuals]
        return self

    def filter(self, func, **kwargs) -> 'Population':
        """filter(f(Individual, **kwargs) -> bool, **kwargs)"""
        self.individuals = [individual for individual in self.individuals if func(individual, **kwargs)]
        return self

    def update(self, func, **kwargs) -> 'Population':
        """update(f(**kwargs), **kwargs)"""
        func(**kwargs)
        return self

    def survive(self, fraction=None, n=None, luck=False) -> 'Population':
        """survive(fraction=None, n=None, luck=False)"""
        if fraction is None:
            if n is None:
                raise ValueError('everyone survives! must provide either "fraction" and/or "n".')
            resulting_size = n
        elif n is None:
            resulting_size = round(fraction*len(self.individuals))
        else:
            resulting_size =  min(round(fraction*len(self.individuals)), n)
        self.evaluate(lazy=True)
        if resulting_size == 0:
            raise RuntimeError('no one survived!')
        if resulting_size > len(self.individuals):
            raise ValueError('everyone survives! must provide "fraction" and/or "n" < population size')
        if luck:
            self.individuals = choices(self.individuals, k=resulting_size,
                                       weights=[individual.fitness for individual in self.individuals])
        else:
            sorted_individuals = sorted(self.individuals, key=lambda x: x.fitness, reverse=self.maximize)
            self.individuals = sorted_individuals[:resulting_size]
        return self

    def breed(self, parent_picker, combiner, population_size=None) -> 'Population':
        """breed(parent_picker=f(Population) -> seq[individuals],
                                             f(*seq[chromosome]) -> chromosome,
                                                                    population_size = None, ** kwargs) <- TODO: kwargs
        """
        if population_size:
            self.intended_size = population_size
        # we copy the population to prevent newly created members to participate in the breed step
        size_before_breed = len(self.individuals)
        for _ in range(len(self.individuals), self.intended_size):
            chromosomes = [individual.chromosome for individual in parent_picker(self.individuals[:size_before_breed])]
            print(chromosomes)
            self.individuals.append(combiner(*chromosomes))
        return self

    def mutate(self, func, **kwargs) -> 'Population':
        """mutate(f(chromosome) -> chromosome, ** kwargs)"""
        for individual in self.individuals:
            individual.mutate(func, **kwargs)
        return self
