########################## Oblique Strategies ############################
OBLIQUE_LIKE_STRATEGIES = [
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
########################## NOTES AND MAJOR KEY INTERVALS ##################
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"] 
MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
DEGREES_MAJOR = ["I", "II", "III", "IV", "V", "VI", "VII"]
DEGREES_MINOR = ["i","ii","iii","iv","v","vi","vii"]

########################## CHORDS ##########################################
TRIADS = ["m","aug","dim"]

# EXTENSIONS
EXTENSIONS = ["9", "11", "13","b9", "#9", "#11", "b13",
              "add9", "add11", "add13", "add2", "add4",
              "sus2", "sus4","maj7","maj9","maj7b5","7","b5"]
AUGMENTED_EXTENSIONS = ["9","11","#9","#11","13", "b13"]
DIMINISHED_EXTENSIONS = ["b9","11","13"]

# DIATONIC PROGRESSIONS
DIATONIC_PROGRESSIONS = {
    "C":  ["C",  "Dm",  "Em",  "F",  "G",  "Am",  "Bdim"],
    "C#": ["C#", "D#m", "Fm",  "F#", "G#", "A#m", "Cdim"],
    "D":  ["D",  "Em",  "F#m", "G",  "A",  "Bm",  "C#dim"],
    "D#": ["D#", "Fm",  "Gm",  "G#", "A#", "Cm",  "Ddim"],
    "E":  ["E",  "F#m", "G#m", "A",  "B",  "C#m", "D#dim"],
    "F":  ["F",  "Gm",  "Am",  "Bb", "C",  "Dm",  "Edim"],
    "F#": ["F#", "G#m", "A#m", "B",  "C#", "D#m", "Fdim"],
    "G":  ["G",  "Am",  "Bm",  "C",  "D",  "Em",  "F#dim"],
    "G#": ["G#", "A#m", "Cm",  "C#", "D#", "Fm",  "Gdim"],
    "A":  ["A",  "Bm",  "C#m", "D",  "E",  "F#m", "G#dim"],
    "A#": ["A#", "Cm",  "Dm",  "D#", "F",  "Gm",  "Adim"],
    "B":  ["B",  "C#m", "D#m", "E",  "F#", "G#m", "A#dim"],
}

# TIME SIGNATURES
TIME_SIGNATURES = ["4/4","3/4","2/4","2/2","5/4","6/4","7/4","6/8","9/8"]

# TEMPOS



