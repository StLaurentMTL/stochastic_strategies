from chords_and_progression import progression_randomizer_hard,ascii_template,strategy_randomizer,time_randomizer


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

if __name__ == "__main__":
    print_banner()
    print("Program starting...")
    progression = progression_randomizer_hard()
    ascii_template(strategy = strategy_randomizer(),
                   progression=progression,
                   time_signature = time_randomizer(),
                   speed = "120 bpm")