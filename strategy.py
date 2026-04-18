import pprint
import random
from musical_variables import (
    NOTES,
    OBLIQUE_LIKE_STRATEGIES,
    MAJOR_INTERVALS,
    DEGREES_MAJOR,
    DEGREES_MINOR, 
    TRIADS,
    EXTENSIONS,
    AUGMENTED_EXTENSIONS,
    DIMINISHED_EXTENSIONS,
    DIATONIC_PROGRESSIONS,
    TIME_SIGNATURES)

class Stochastic_Progression():

    def __init__(self,key = None, progression = None, strategy = None,tempo = None):

        # Initializing Key
        self._key = None

        # Initialzing Progression
        self._progression = None

        # Initial Strategy
        self._strategy = None

        # Time Signature
        self._timesig = None

        # Tempo
        self._tempo = None
    
    def progression_randomizer_easy(self):

        """
        Generates a chord progression in any random key, but begins with a 
        diatonic chord base and has a low probability of chromaticism
        
        """
        progression = []

        # Thresholds
        extensions_threshold = random.uniform(0,.5)
        chromatic_threshold = random.uniform(0,.1)
        triad_threshold = random.uniform(0,1)
        
        # Setting Key
        self._key = random.choice(list(DIATONIC_PROGRESSIONS.keys()))
        key_progression = DIATONIC_PROGRESSIONS[self._key]

        for i in range(random.randrange(2,8,1)):

            if random.uniform(0,1) <= chromatic_threshold:
                chord = random.choice(NOTES)
                triad = None

                # Selecting triad
                if random.uniform(0,1) <= triad_threshold:
                    triad = random.choices(TRIADS,weights = [80,10,10],k = 1)[0]
                    chord += triad
            else:
                chord = random.choice(key_progression)

            if random.uniform(0,1) <= extensions_threshold:

                chord += random.choice(EXTENSIONS)
            
            progression.append(chord)

        self._progression = " - ".join(progression)        

    def progression_randomizer_hard(self):

        """
        Generates a chord progression in any random key. (HARD DIFFICULTY)
        
        """

        progression = []

        # Thresholds
        extensions_threshold = random.uniform(0,1)
        triad_threshold = random.uniform(0,1)

        # Determining length of chord progression
        for i in range(random.randrange(2,8,1)):

            # Selecting the chord degree
            chord = random.choice(NOTES)
            triad = None

            # Selecting triad
            if random.uniform(0,1) <= triad_threshold:
                triad = random.choices(TRIADS,weights = [80,10,10],k = 1)[0]
                chord = chord + triad
            
            # Adding in extensions
            if random.uniform(0,1) <= extensions_threshold:

                if triad == "dim":
                    chord += random.choice(DIMINISHED_EXTENSIONS)
                elif triad == "aug":
                    chord += random.choice(AUGMENTED_EXTENSIONS)
                else:
                    chord += random.choice(EXTENSIONS)

            progression.append(chord)
        
        self._progression = " - ".join(progression)

    def build_card(self, speed="120 bpm") -> str:
        width = 52

        def center(text):
            return f"│  {text.center(width)}  │"

        lines = []
        lines.append(f"┌{'─' * (width + 4)}┐")
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(f"│  {'✦  S T O C H A S T I C   S T R A T E G I E S  ✦'.center(width)}  │")
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(f"├{'─' * (width + 4)}┤")
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(center(self._strategy or ""))
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(f"├{'─' * (width + 4)}┤")
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(center(self._progression or ""))
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(f"├{'─' * (width + 4)}┤")
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(center(f"{self._timesig}    ♩= {self._tempo}"))
        lines.append(f"│{' ' * (width + 4)}│")
        lines.append(f"└{'─' * (width + 4)}┘")

        return "\n".join(lines)

    def strategy_randomizer(self):

        self._strategy = random.choice(OBLIQUE_LIKE_STRATEGIES)

    def time_randomizer(self):

        self._timesig =  random.choice(TIME_SIGNATURES)

    def tempo_randomizer(self):

        self._tempo = random.randint(50,200)
