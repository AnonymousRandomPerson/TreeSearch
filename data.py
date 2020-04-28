# coding: utf-8

import csv

pokemonFile = 'pokemonSS.csv'
trainersFile = 'trainersSS.csv'

class Data:
    """Stores data about Battle Tree Pokémon."""

    def __init__(self):
        """Initializes the data storage."""

        self.sets = {}
        with open(pokemonFile, 'r') as csvFile:
            pokemonReader = csv.reader(csvFile)
            for row in pokemonReader:
                set = Set(row)
                self.sets[set.name] = set

        self.trainers = {}
        with open(trainersFile, 'r') as csvFile:
            trainerReader = csv.reader(csvFile)
            for row in trainerReader:
                trainer = Trainer(self, row)
                self.trainers[trainer.name.lower()] = trainer

    def getTrainer(self, name):
        """
        Gets a Trainer's data.

        Args:
            The name of the Trainer.
        """
        name = name.lower()
        if name in self.trainers:
            return self.trainers[name]
        return None

    def getSet(self, name):
        """
        Gets a set's data.

        Args:
            The name of the set.
        """
        if name in self.sets:
            return self.sets[name]
        return None

class Set:
    """Data about a specific Pokémon set."""

    def __init__(self, row):
        """
        Initializes a set.

        Args:
            row: The CSV data for the set.
        """

        self.name = row[0]
        self.pokemon = row[0][:row[0].index('-')]
        self.nature = row[1]
        self.item = row[2]
        self.moves = tuple(row[i] for i in range(3, 7))
        self.evs = row[7]

    def __repr__(self):
        """Returns the set's name."""
        return self.name

class Trainer:
    """Data about a specific Trainer."""

    def __init__(self, data, row):
        """
        Initializes a Trainer.

        Args:
            data: The data object containing Pokémon data.
            row: The CSV data for the Trainer.
        """

        self.name = row[0]
        allPokemon = row[1].split(',')
        allPokemon.sort()
        self.sets = []
        self.dynamax = {}
        for pokemon in allPokemon:
            isDynamax = False
            for dynamaxKeyword in ['-Dynamax', '-Gigantamax']:
                if dynamaxKeyword in pokemon:
                    pokemon = pokemon.replace(dynamaxKeyword, '')
                    isDynamax = True
                    break

            pokemonSet = data.getSet(pokemon)
            self.sets.append(pokemonSet)
            if isDynamax:
                self.dynamax[pokemonSet.name] = dynamaxKeyword

    def __repr__(self):
        """Returns the Trainer's name."""
        return self.name

    def getSets(self, name):
        """
        Gets the possible Pokémon sets for the Trainer.

        Args:
            name: The name of the Pokémon to get possible sets for.
        """

        sets = []
        name = name.lower()
        if name:
            for pokemonSet in self.sets:
                lowerName = pokemonSet.name.lower()
                if lowerName.startswith(name):
                    sets.append(pokemonSet)
        return sets