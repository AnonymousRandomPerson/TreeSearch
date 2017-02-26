# coding: utf-8

import csv

class Data:
    """Stores data about Battle Tree Pokémon."""

    def __init__(self):
        """Initializes the data storage."""

        self.sets = {}
        with open('pokemon.csv', 'rb') as csvFile:
            pokemonReader = csv.reader(csvFile)
            for row in pokemonReader:
                set = Set(row)
                self.sets[set.name] = set

        self.trainers = {}
        with open('trainers.csv', 'rb') as csvFile:
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

        self.name = row[1]
        self.pokemon = row[1][:-2]
        self.nature = row[2]
        self.item = row[3]
        self.moves = tuple(row[i] for i in range(4, 8))
        self.evs = row[8]

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
        
        unsplit = row[0]

        splitIndex = unsplit.find(" - ")
        self.name = unsplit[:splitIndex]
        allPokemon = unsplit[splitIndex + 3:].split(", ")
        allPokemon.sort()
        self.sets = []
        for pokemon in allPokemon:
            self.sets.append(data.getSet(pokemon))

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
            for set in self.sets:
                lowerName = set.name.lower()
                if lowerName.startswith(name):
                    sets.append(set)
        return sets