import time
import typer
from rich.prompt import Prompt
from rich.progress import track
from strategy import Stochastic_Progression


def print_banner():
    print(r"""
          
 _____ _             _               _   _        _____ _             _             _           
/  ___| |           | |             | | (_)      /  ___| |           | |           (_)          
\ `--.| |_ ___   ___| |__   __ _ ___| |_ _  ___  \ `--.| |_ _ __ __ _| |_ ___  __ _ _  ___  ___ 
 `--. \ __/ _ \ / __| '_ \ / _` / __| __| |/ __|  `--. \ __| '__/ _` | __/ _ \/ _` | |/ _ \/ __|
/\__/ / || (_) | (__| | | | (_| \__ \ |_| | (__  /\__/ / |_| | | (_| | ||  __/ (_| | |  __/\__ \
\____/ \__\___/ \___|_| |_|\__,_|___/\__|_|\___| \____/ \__|_|  \__,_|\__\___|\__, |_|\___||___/
                                                                               __/ |            
                                                                             |___/      

A Songwriting Tool inspired by David Bowie, Brian Eno, and Stochastics! 
                
""")

PROMPTS = ["Shuffling the Harmonies","Randomizing Inspiration","Time is a crooked bow"]

app = typer.Typer()
@app.command()
    
def main():

    running = True
    
    while running == True:

        difficulty_type = Prompt.ask("Would you like a challenge? Or Something more Relaxed?",
                                     choices = ["Challenge","Relaxed"])

        Strategy = Stochastic_Progression()
        Strategy.progression_randomizer_hard()
        Strategy.strategy_randomizer()
        Strategy.time_randomizer() 
        Strategy.tempo_randomizer()

        if difficulty_type == "Challenge":

            Strategy.progression_randomizer_hard()
        
        if difficulty_type == "Relaxed":

            Strategy.progression_randomizer_easy()

        for prompt in PROMPTS:

            for a in track(range(100),description = prompt):

                time.sleep(0.01)

        print("=================YOUR CREATIVE DILEMMA================")
        card = Strategy.build_card()
        print(card)

        card_save = Prompt.ask("Would you like to save your card?",
                               choices = ["Y","N"])
        
        if card_save == "Y":
            filename = Prompt.ask("Enter filename", default="creative_card")

            with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                f.write(card)

            print(f"Saved to {filename}.txt")
        
        if card_save == "N":

            continue_opt = Prompt.ask("Create a new card?",
                                      choices = ["Y","N"],
                                      default = "Y")
            if continue_opt == "N":
                break
        
if __name__ == "__main__":
    
    print_banner()

    app()