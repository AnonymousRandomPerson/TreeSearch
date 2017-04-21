# coding: utf-8

from Tkinter import *
from data import *

class Screen:

    """The main GUI screen."""

    def __init__(self):
        """Initializes the screen elements."""
        self.error = None
        self.trainer = None
        self.secondTrainer = None
        self.battleType = None
        self.pokemonEntry = []
        self.setObjects = []
        self.updateEntries = []
        self.updateFunctions = (self.update0, self.update1, self.update2, self.update3)

        # Moves and items that will be highlighted red.
        self.redFlags = []
        self.flagMegas = True
        self.flagZ = True

        self.root = Tk()
        self.root.wm_title("Tree Search")

        self.searchFrame = Frame(self.root)
        self.searchFrame.grid(row=0, column=0, sticky=E)
        self.trainerEntry = self.createLabeledEntry(0, "Trainer")
        self.pokemonEntry.append(self.createLabeledEntry(1, "Pokémon 1"))
        self.pokemonEntry.append(self.createLabeledEntry(2, "Pokemon 2"))

        def searchEvent(event):
            """
            Searches for a Trainer's sets.

            Args:
                event: The event that invoked this function.
            """
            self.searchTrainer()
        self.trainerEntry.bind("<Return>", searchEvent)

        for entry in self.pokemonEntry:
            entry.bind("<Return>", searchEvent)

        searchButton = Button(self.searchFrame, text="Search", command=self.searchTrainer, takefocus=False)
        searchButton.grid(row=0, column=2)

        self.data = Data()

        self.initSearch = False

        self.root.mainloop()

    def initAfterSearch(self):
        """Initializes the add Pokémon entry and table headers after a Trainer is searched for."""
        self.addPokemonEntry = self.createLabeledEntry(3, "Add Pokémon")

        def addEvent(event):
            """
            Adds another Pokémon to the Trainer.

            Args:
                event: The event that invoked this function.
            """
            self.addPokemon()

        self.addPokemonEntry.bind("<Return>", addEvent)

        addButton = Button(self.searchFrame, text="Add", command=self.addPokemon, takefocus=False)
        addButton.grid(row=3, column=2)

        self.setFrame = Frame(self.root)
        self.setFrame.grid(row=1, column=0)
        rowNames = ("Set", "Item", "Move 1", "Move 2", "Move 3", "Move 4", "Nature", "EVs")
        for i, name in enumerate(rowNames):
            label = Label(self.setFrame, text=name).grid(row=0, column=i)

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
        trainers = str.split(self.trainerEntry.get(), ",")
        if not trainers:
            return
        trainer = self.data.getTrainer(trainers[0])
        
        secondTrainer = None
        if len(trainers) > 1:
            secondTrainer = self.data.getTrainer(trainers[1])
            if not secondTrainer:
                self.setErrorText("Trainer not found: " + trainers[1])
                return

        if not trainer:
            self.setErrorText("Trainer not found: " + trainers[0])
            return
        
        sets = []
        for entry in self.pokemonEntry:
            pokemon = entry.get()
            currentSet = self.getSets(pokemon, trainer, secondTrainer)
            if len(currentSet) == 0:
                if len(sets) == 0:
                    self.setErrorText("Pokémon not found: " + pokemon)
                    return
            else:
                sets.append(currentSet)
        self.trainer = trainer
        self.secondTrainer = secondTrainer
        self.sets = sets

        self.updateBattleType(len(sets))

        self.setErrorText("")
        for entry in self.pokemonEntry:
            entry.delete(0, END)

        if not self.initSearch:
            self.initSearch = True
            self.initAfterSearch()

        self.displaySets()

    def getSets(self, pokemon, trainer, secondTrainer):
        """
        Gets the sets that can be used by a Trainer or two.

        Args:
            pokemon: The Pokémon to get sets for.
            trainer: The first Trainer to get sets for.
            secondTrainer: The second Trainer to get sets for, or None to not have a second Trainer.

        Returns:
            The sets that can be used by a Trainer or two. 
        """
        currentSet = trainer.getSets(pokemon)
        if secondTrainer:
            for set in secondTrainer.getSets(pokemon):
                if set not in currentSet:
                    currentSet.append(set)
        return currentSet

    def addPokemon(self):
        """Adds Pokémon to the Trainer."""
        
        if not self.trainer:
            self.setErrorText("No Trainer selected.")
            return

        allPokemon = str.split(self.addPokemonEntry.get(), ",")
        newEntry = ""
        error = ""
        full = False
        modified = True

        def addToError(error, newError):
            """
            Adds a new error to the current error string.

            Args:
                error: The original error string.
                newError: The new error string to add.

            Returns:
                The new error string.
            """
            if error:
                error += "\n" + newError
            else:
                error = newError
            return error

        for pokemon in allPokemon:
            if len(self.sets) >= 4:
                error = addToError(error, "Too many Pokémon.")
                full = True
                break

            currentError = self.addSinglePokemon(pokemon)

            if currentError:
                error = addToError(error, currentError)
                if newEntry:
                    newEntry += " "
                newEntry += pokemon
            else:
                modified = True
            

        self.setErrorText(error)
        if full or modified:
            self.addPokemonEntry.delete(0, END)
            if newEntry:
                self.addPokemonEntry.insert(END, newEntry)
        
            if modified:
                self.displaySets()

    def addSinglePokemon(self, pokemon):
        """
        Adds one Pokémon to the Trainer.

        Args:
            pokemon: The Pokémon to add.
        
        Returns:
            An error message if the operation failed.
            None if the operation succeeded.
        """
        currentSets = self.getSets(pokemon, self.trainer, self.secondTrainer)

        if not self.secondTrainer:
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
            return "Pokémon not found: " + pokemon + "."
            return False

        for set in self.sets:
            if set[0].pokemon == currentSets[0].pokemon:
                return "Duplicate Pokémon."

        self.sets.append(currentSets)
        return None

    def displaySets(self):
        """Displays the current sets on the screen."""

        for object in self.setObjects + self.updateEntries:
            if object:
                object.grid_forget()
        self.setObjects = []
        self.updateEntries = []

        def updateEvent(event):
            """
            Updates the possible Pokémon at a certain slot.

            Args:
                event: The event that invoked this function.
            """
            for i in range(len(self.updateEntries)):
                if event.widget == self.updateEntries[i]:
                    self.updatePokemon(i)
                    break

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

            numPokemon = len(pokemon)
            if numPokemon > 1:
                firstRow = currentRow - numPokemon
                entry = Entry(self.setFrame)
                entry.grid(row=firstRow, column=i+1)
                entry.bind("<Return>", updateEvent)
                self.updateEntries.append(entry)

                button = Button(self.setFrame, text="Update", command=self.updateFunctions[slot], takefocus=False)
                button.grid(row=firstRow, column=i+2)
                self.setObjects.append(button)
            else:
                self.updateEntries.append(None)

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
        compareField = currentEntry.get().lower()
        for set in sets:
            fields = (set.name, set.item, set.moves[0], set.moves[1], set.moves[2], set.moves[3])
            valid = False
            for field in fields:
                lowerField = field.lower()
                if lowerField != "" and lowerField.startswith(compareField):
                    valid = True
                    break
            if valid:
                newSets.append(set)
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

    def updateBattleType(self, battleType):
        """
        Updates the type of battle that is being used.

        Args:
            battleType: The type of battle that is being used.
        """

        if self.battleType != battleType:
            self.battleType = battleType
            if battleType == 1:
                self.redFlags = ["Bright Powder", "Choice Scarf", "Custap Berry", "Focus Band", "Focus Sash", "Lax Incense", "Quick Claw"]
                self.redFlags += ["Aurora Veil", "Light Screen", "Reflect", "Tailwind", "Trick Room"]
                self.redFlags += ["Fissure", "Guillotine", "Horn Drill", "Sheer Cold"]
                self.redFlags += ["Grass Whistle", "Hypnosis", "Lovely Kiss", "Sing", "Sleep Powder", "Spore"]
                self.redFlags += ["Double Team", "Minimize"]
                self.redFlags += ["Counter", "Metal Burst", "Mirror Coat"]
            elif battleType == 2:
                self.redFlags = ["Bright Powder", "Choice Scarf", "Custap Berry", "Focus Band", "Focus Sash", "Lax Incense", "Occa Berry", "Quick Claw"]
                self.redFlags += ["Accelerock", "Aqua Jet", "Bullet Punch", "Extreme Speed", "Fake Out", "Feint", "First Impression", "Ice Shard", "Mach Punch", "Quick Attack", "Shadow Sneak", "Sucker Punch", "Vacuum Wave", "Water Shuriken"]
                self.redFlags += ["Hail", "Light Screen", "Rain Dance", "Sandstorm", "Tailwind", "Trick Room", "Wide Guard"]
                self.redFlags += ["Fissure", "Guillotine", "Horn Drill", "Rock Slide", "Sheer Cold"]
                self.redFlags += ["Disable", "Grass Whistle", "Hypnosis", "Lovely Kiss", "Sing", "Sleep Powder", "Spore", "Torment"]
                self.redFlags += ["Double Team", "Minimize"]
                self.redFlags += ["Metal Burst", "Mirror Coat"]