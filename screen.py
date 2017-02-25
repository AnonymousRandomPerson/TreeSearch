# coding: utf-8

from Tkinter import *
from data import *

class Screen:
    """The main GUI screen."""

    def __init__(self):
        """Initializes the screen elements."""
        self.error = None
        self.trainer = None
        self.pokemonEntry = []
        self.setObjects = []
        self.updateEntries = []
        self.updateFunctions = (self.update0, self.update1, self.update2, self.update3)

        # Moves and items that will be highlighted red.
        self.redFlags = ["Bright Powder", "Choice Scarf", "Custap Berry", "Focus Band", "Focus Sash", "Lax Incense", "Occa Berry", "Quick Claw"]
        self.redFlags += ["Accelerock", "Aqua Jet", "Bullet Punch", "Extreme Speed", "Fake Out", "Feint", "First Impression", "Ice Shard", "Mach Punch", "Quick Attack", "Shadow Sneak", "Sucker Punch", "Vacuum Wave", "Water Shuriken"]
        self.redFlags += ["Hail", "Light Screen", "Rain Dance", "Sandstorm", "Tailwind", "Trick Room", "Wide Guard"]
        self.redFlags += ["Fissure", "Guillotine", "Horn Drill", "Rock Slide", "Sheer Cold"]
        self.redFlags += ["Disable", "Grass Whistle", "Hypnosis", "Lovely Kiss", "Sing", "Sleep Powder", "Spore", "Torment"]
        self.redFlags += ["Double Team", "Minimize"]
        self.flagMegas = True
        self.flagZ = True

        self.root = Tk()

        self.searchFrame = Frame(self.root)
        self.trainerEntry = self.createLabeledEntry(0, "Trainer")
        self.pokemonEntry.append(self.createLabeledEntry(1, "Pokémon 1"))
        self.pokemonEntry.append(self.createLabeledEntry(2, "Pokemon 2"))
        self.addPokemonEntry = self.createLabeledEntry(3, "Add Pokémon")

        button = Button(self.searchFrame, text="Search", command=self.searchTrainer).grid(row=0, column=2)
        button = Button(self.searchFrame, text="Add", command=self.addPokemon).grid(row=3, column=2)
        self.searchFrame.grid(row=0, column=0, sticky=E)
        
        debug = True
        if debug:
            self.trainerEntry.insert(0, "Red")
            self.pokemonEntry[0].insert(0, "Lapras")
            self.pokemonEntry[1].insert(0, "Venusaur")
            self.addPokemonEntry.insert(0, "Charizard")

        self.setErrorText("")

        self.setFrame = Frame(self.root)
        self.setFrame.grid(row=1, column=0)
        rowNames = ("Set", "Item", "Move 1", "Move 2", "Move 3", "Move 4", "Nature", "EVs")
        for i, name in enumerate(rowNames):
            label = Label(self.setFrame, text=name).grid(row=0, column=i)

        self.data = Data()

        self.root.mainloop()

    def createLabeledEntry(self, entryRow, name):
        """
        Creates an entry with a label to the left of it.
        
        Args:
            entryRow: The row that the entry should be on.
            name: The name of the entry.

        Returns:
            The created entry.
        """

        entry = Entry(self.searchFrame)
        entry.grid(row=entryRow, column=1)
        label = Label(self.searchFrame, text=name)
        label.grid(row=entryRow, column=0)

        return entry

    def setErrorText(self, errorText):
        """
        Sets the contents of the error message.

        Args:
            errorText: The contents of the error message.
        """
        if self.error:
            self.error.grid_forget()
        self.error = Label(self.searchFrame, text=errorText, fg="red")
        self.error.grid(row=4, column=1)

    def searchTrainer(self):
        """Searches for a Trainer's sets."""
        trainer = self.data.getTrainer(self.trainerEntry.get())
        if not trainer:
            self.setErrorText("Trainer not found.")
            return
        
        sets = []
        for entry in self.pokemonEntry:
            pokemon = entry.get()
            currentSet = trainer.getSets(pokemon)
            if len(currentSet) == 0:
                self.setErrorText("Pokémon not found: " + pokemon)
                return
            sets.append(currentSet)
        self.trainer = trainer
        self.sets = sets

        self.setErrorText("")
        self.trainerEntry.delete(0, END)
        for entry in self.pokemonEntry:
            entry.delete(0, END)

        self.displaySets()

    def addPokemon(self):
        """Adds another Pokémon to the Trainer."""
        
        if not self.trainer:
            self.setErrorText("No Trainer selected.")
            return

        if len(self.sets) >= 4:
            self.setErrorText("Too many Pokémon.")
            return

        pokemon = self.addPokemonEntry.get()
        currentSets = self.trainer.getSets(pokemon)

        # Remove sets that are rendered invalid by item clause.
        removeSet = []
        for set in self.sets:
            if len(set) > 1:
                continue

            for current in currentSets:
                if current.item == set[0].item:
                    removeSet.append(current)
        for set in removeSet:
            currentSets.remove(set)

        if len(currentSets) == 0:
            self.setErrorText("Pokémon not found: " + pokemon + ".")
            return

        for set in self.sets:
            if set[0].pokemon == currentSets[0].pokemon:
                self.setErrorText("Duplicate Pokémon.")
                return

        self.sets.append(currentSets)
        self.addPokemonEntry.delete(0, END)
        
        self.displaySets()

    def displaySets(self):
        """Displays the current sets on the screen."""

        for object in self.setObjects + self.updateEntries:
            object.grid_forget()
        self.setObjects = []
        self.updateEntries = []

        currentRow = 1
        for slot, pokemon in enumerate(self.sets):
            for set in pokemon:
                fields = (set.name, set.item, set.moves[0], set.moves[1], set.moves[2], set.moves[3], set.nature, set.evs)
                for i, field in enumerate(fields):
                    color = "black"
                    if field in self.redFlags:
                        color = "red"
                    elif field == set.item:
                        if self.flagMegas and field[-3:] == "ite" and field != "Eviolite":
                            color = "red"
                        elif self.flagZ and field[-2:] == " Z":
                            color = "red"
                    label = Label(self.setFrame, text=field, fg=color)
                    self.setObjects.append(label)
                    label.grid(row=currentRow, column=i)

                currentRow += 1

            firstRow = currentRow - len(pokemon)
            entry = Entry(self.setFrame)
            entry.grid(row=firstRow, column=i+1)
            self.updateEntries.append(entry)

            button = Button(self.setFrame, text="Update", command=self.updateFunctions[slot])
            button.grid(row=firstRow, column=i+2)
            self.setObjects.append(button)

            label = Label(self.setFrame, text="")
            label.grid(row=currentRow, column=0)
            self.setObjects.append(label)
            currentRow += 1

    def updatePokemon(self, number):
        """
        Updates the possible Pokémon at a certain slot.
        
        Args:
            number: The slot number of the Pokémon to update.
        """
        sets = self.sets[number]
        if len(sets) == 1:
            return

        newSets = []
        currentEntry = self.updateEntries[number]
        compareField = currentEntry.get()
        for set in sets:
            fields = (set.name, set.item, set.moves[0], set.moves[1], set.moves[2], set.moves[3])
            valid = False
            for field in fields:
                if field != "" and field == compareField:
                    valid = True
                    break
            if valid:
                newSets.append(set)
                break
        if len(newSets) > 0:
            self.sets[number] = newSets
            self.displaySets()

    def update0(self):
        """Updates the party Pokémon at index 0."""

        self.updatePokemon(0)

    def update1(self):
        """Updates the party Pokémon at index 1."""

        self.updatePokemon(1)

    def update2(self):
        """Updates the party Pokémon at index 2."""

        self.updatePokemon(2)

    def update3(self):
        """Updates the party Pokémon at index 3."""

        self.updatePokemon(3)