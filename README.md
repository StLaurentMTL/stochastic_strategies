# Stochastic Strategies
## A Songwriting Tool inspired by David Bowie, Brian Eno, and Stochastics
In 1976, following a tumultuous year dealing with severe addictions, David Bowie decamped to the city of Berlin in search of 
musical reinvention with the legendary producer Brian Eno. During their time recording the albums _Low_, _Heroes_, and _Lodger_, 
Bowie and Eno sought inspiration from a deck of bamboo cards called _Oblique Strategies_. These cards would have mysterious but thought
provoking remarks that the artist would then have to decipher in their music. Since their use by Bowie and Eno, many artists have used 
the cards in their own albums, including LCD Soundsystem, Phoenix, The B-52s, MGMT, and Bauhaus. 

![Bowie,Eno,Fripp photo by Sky TV](https://github.com/StLaurentMTL/stochastic_strategies/blob/main/photos/david_brian.jpg)

__Stochastic Strategies__ is a simple algorithm I wrote that takes inspiration from *Oblique Strategies* that songwriters can use to challenge themselves and 
their songwriting. It can generate interesting chordal harmonies, suggest fun time signatures, and even suggest an "Oblique-like" prompt to boot!

## Table of Contents
- [Demonstrations](#demonstrations)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Tips](#tips)
- [Example Session](#example-session)

## Demonstrations
Here I received the prompt __"Replace intent with procedure"__ with the generated chord progression of $Ebadd11 - Gm - Ab$ 
in 7/4 time and a BPM 82 (https://www.youtube.com/shorts/w0HZ1BGVD1s)
![Card Example 1](https://github.com/StLaurentMTL/stochastic_strategies/blob/main/photos/card2exp.jpg)

Here I received the prompt __"Limit time to force structural decisions"__ with the generated chord progression of $Dm - Db11$ in 5/4 time and a BPM of 106 (https://www.youtube.com/shorts/Yuv4bGoAMFI)
![Card Example 2](https://github.com/StLaurentMTL/stochastic_strategies/blob/main/photos/card1exp.jpg)

## Requirements

- Python 3.8+
- The following packages:

```bash
pip install typer rich
```

You'll also need the `strategy.py` module (containing the `Stochastic_Progression` class) in the same directory as `main.py`.

---

## Installation

Clone or download the project files, then install dependencies:

```bash
pip install typer rich
```

---

## Usage

Run the app from your terminal:

```bash
python main.py
```

### Step-by-step

1. **Choose a difficulty**

   When prompted, type either `Challenge` or `Relaxed`:

   - **Challenge** — generates a harder chord progression much more likely to be chromatic and feature odd time signatures like 5/4, 7/8, or 9/8. 
   - **Relaxed** — generates a more approachable progression that increases the probalities of generating a progression that remains in key, minimizes the probabilties of receiving chromatic extensions or triads

2. **Receive your Creative Dilemma**

   Your card is printed to the terminal. It contains a randomized combination of:
   - A chord progression
   - A "oblique"-like songwriting strategy
   - A time signature
   - A tempo

3. **Save your card (optional)**

   You'll be asked if you want to save the card:
   - Enter `Y` to save — you'll be prompted for a filename (defaults to `creative_card`). The card is saved as a `.txt` file in your current directory.
   - Enter `N` to skip saving.

4. **Generate another card**

   If you chose not to save, you'll be asked whether you want to generate a new card. Enter `Y` to loop back to the start, or `N` to exit.

---
## Tips
- Run it multiple times — the stochastic engine is designed to surprise you.
- Use the **Relaxed** mode when you want to stay in familiar harmonic territory.
- Use **Challenge** mode to push yourself into unfamiliar progressions.
- Save cards that feel interesting, even if you don't use them right away. They make great starting points later.

## Example Session
```bash
/  ___| |           | |             | | (_)      /  ___| |           | |           (_)
\ `--.| |_ ___   ___| |__   __ _ ___| |_ _  ___  \ `--.| |_ _ __ __ _| |_ ___  __ _ _  ___  ___
 `--. \ __/ _ \ / __| '_ \ / _` / __| __| |/ __|  `--. \ __| '__/ _` | __/ _ \/ _` | |/ _ \/ __|
/\__/ / || (_) | (__| | | | (_| \__ \ |_| | (__  /\__/ / |_| | | (_| | ||  __/ (_| | |  __/\__ \
\____/ \__\___/ \___|_| |_|\__,_|___/\__|_|\___| \____/ \__|_|  \__,_|\__\___|\__, |_|\___||___/
                                                                               __/ |
                                                                             |___/

A Songwriting Tool inspired by David Bowie, Brian Eno, and Stochastics!


Would you like a challenge? Or Something more Relaxed? [Challenge/Relaxed]: Challenge
Shuffling the Harmonies ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
Randomizing Inspiration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
Time is a crooked bow ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
=================YOUR CREATIVE DILEMMA================
┌────────────────────────────────────────────────────────┐
│                                                        │
│    ✦  S T O C H A S T I C   S T R A T E G I E S  ✦     │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│   Assume the system is already optimal and break it    │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│        D#add9 - Bmb9 - A# - Bmaj9 - B - A# - C         │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│                      6/8    ♩= 68                      │
│                                                        │
└────────────────────────────────────────────────────────┘
Would you like to save your card? [Y/N]: N
Create a new card? [Y/N] (Y): N
```
