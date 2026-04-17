import pprint
import random

# class Stochastic_Progression():

#     def __init__

# Oblique Strategies
oblique_like_strategies = [
    "Invert the assumption driving the current decision",
    "Remove the most obvious element and proceed",
    "Replace control with constraint",
    "Increase randomness by one degree",
    "Act as if the opposite constraint is true",
    "Simplify until meaning starts to degrade, then restore one element",
    "Treat failure as primary input",
    "Force a choice between two unattractive options",
    "Change only one variable and observe outcome",
    "Translate the problem into a different domain",
    "Remove all but one tool or resource",
    "Add an unnecessary constraint and obey it",
    "Redo the last step in a different order",
    "Assume the system is already optimal and break it",
    "Work backward from a desired failure state",
    "Replace intent with procedure",
    "Randomize the starting condition",
    "Limit time to force structural decisions",
    "Externalize the decision to a random mechanism",
    "Ignore the stated objective and pursue the hidden one",
    "Make the smallest possible visible change",
    "Amplify an error until it becomes structure",
    "Freeze one parameter and vary everything else",
    "Swap roles between cause and effect",
    "Pretend the system belongs to someone else"
]

# NOTES AND MAJOR KEY INTERVALS
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"] 
MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
DEGREES_MAJOR = ["I", "II", "III", "IV", "V", "VI", "VII"]
DEGREES_MINOR = ["i","ii","iii","iv","v","vi","vii"]

# CHORD TYPES
TRIADS = ["m","aug","dim"]
EXTENSIONS = ["9", "11", "13","b9", "#9", "#11", "b13",
              "add9", "add11", "add13", "add2", "add4",
              "sus2", "sus4","maj7","maj9","maj7b5","7","b5"]

AUGMENTED_EXTENSIONS = ["9","11","#9","#11","13", "b13"]
DIMINISHED_EXTENSIONS = ["b9","11","13"]

# TIME SIGNATURES
TIME_SIGNATURES = ["4/4","3/4","2/4","2/2","5/4","6/4","7/4","6/8","9/8"]

def major_key_map(root: str):

    root_index = NOTES.index(root)

    result = {}

    i = 0
    while i < len(DEGREES_MAJOR):
        degree = DEGREES_MAJOR[i]
        interval = MAJOR_INTERVALS[i]

        note_index = root_index + interval
        note_index = note_index % 12

        note = NOTES[note_index]
        result[degree] = note

        i += 1

    return result

def progression_randomizer_hard():

    """
    Generates a chord progression in any random key
    
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
        if random.uniform(0,1) >= triad_threshold:
            triad = random.choices(TRIADS,weights = [80,10,10],k = 1)[0]
            chord = chord + triad
        
        # Adding in extensions
        if random.uniform(0,1) >= extensions_threshold:

            if triad == "dim":
                chord += random.choice(DIMINISHED_EXTENSIONS)
            elif triad == "aug":
                chord += random.choice(AUGMENTED_EXTENSIONS)
            else:
                chord += random.choice(EXTENSIONS)

        progression.append(chord)
    
    return " - ".join(progression)

def ascii_template(strategy = "Replace control with constraint",
                   progression = "C - Am - F - G",
                   time_signature = "4/4",
                   speed = "120 bpm"):

    width = 52
    def center(text):
        return f"│  {text.center(width)}  │"
    
    print(f"┌{'─' * (width + 4)}┐")
    print(f"│{' ' * (width + 4)}│")
    print(f"│  {'✦  S T O C H A S T I C   S T R A T E G I E S  ✦'.center(width)}  │")
    print(f"│{' ' * (width + 4)}│")
    print(f"├{'─' * (width + 4)}┤")
    print(f"│{' ' * (width + 4)}│")
    print(center(strategy))
    print(f"│{' ' * (width + 4)}│")
    print(f"├{'─' * (width + 4)}┤")
    print(f"│{' ' * (width + 4)}│")
    print(center(progression))
    print(f"│{' ' * (width + 4)}│")
    print(f"├{'─' * (width + 4)}┤")
    print(f"│{' ' * (width + 4)}│")
    print(center(f"{time_signature}    ♩= {speed}"))
    print(f"│{' ' * (width + 4)}│")
    print(f"└{'─' * (width + 4)}┘")

def strategy_randomizer():

    return random.choice(oblique_like_strategies)

def time_randomizer():

    return random.choice(TIME_SIGNATURES)
