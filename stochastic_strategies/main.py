import urllib.parse
import json
import functools
import http.server
import socketserver
import time
import webbrowser
from pathlib import Path

import typer
from rich.prompt import Prompt
from rich.progress import track

from stochastic_strategies.strategy import StochasticProgression


def print_banner() -> None:
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


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Intercept API calls
        if self.path.startswith("/api/generate"):
            parsed_path = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            difficulty = query.get("difficulty", ["relaxed"])[0]

            # Generate via Python backend
            strategy = StochasticProgression()
            strategy.strategy_randomizer()
            strategy.time_randomizer()
            strategy.tempo_randomizer()

            if difficulty == "challenge":
                strategy.progression_randomizer_hard()
            else:
                strategy.progression_randomizer_easy()

            response_data = {
                "difficulty": difficulty,
                "strategy": strategy._strategy,
                "timesig": strategy._timesig,
                "tempo": strategy._tempo,
                "keyName": strategy._key,
                "progression": strategy._progression,
                "entropy": strategy._entropy,
                "maxEntropy": 2.807354922, # log2(7)
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            # Serve static files (like your HTML) normally
            super().do_GET()


PROMPTS: list[str] = [
    "Shuffling the Harmonies",
    "Randomizing Inspiration",
    "Time is a crooked bow",
]

# The browser front end (ticket machine UI) lives in the templates folder.
FRONTEND_DIR = FRONTEND_DIR = Path(__file__).resolve().parent.parent / "templates"
FRONTEND_FILE = "stochastic-strategies-ticket.html"

app = typer.Typer()


def launch_web() -> None:
    """Serve the ticket-machine front end locally and open it in a browser."""
    frontend_path = FRONTEND_DIR / FRONTEND_FILE

    if not frontend_path.exists():
        typer.echo(f"Couldn't find {FRONTEND_FILE} in {FRONTEND_DIR}.")
        return

    handler = functools.partial(APIHandler, directory=str(FRONTEND_DIR))

    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        url = f"http://127.0.0.1:{port}/{FRONTEND_FILE}"
        typer.echo(f"Opening the ticket machine at {url}")
        typer.echo("Press Ctrl+C here to stop the server.")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            typer.echo("\nShutting down. Alles Gute!")


def run_terminal_loop() -> None:
    """The original prompt-driven terminal experience."""
    while True:
        difficulty_type = Prompt.ask(
            "Would you like a challenge? Or Something more Relaxed?",
            choices=["Challenge", "Relaxed"],
        )

        strategy = StochasticProgression()
        strategy.strategy_randomizer()
        strategy.time_randomizer()
        strategy.tempo_randomizer()

        if difficulty_type == "Challenge":
            strategy.progression_randomizer_hard()
        else:
            strategy.progression_randomizer_easy()

        for prompt in PROMPTS:
            for _ in track(range(100), description=prompt):
                time.sleep(0.01)

        print("=================YOUR CREATIVE DILEMMA================")
        card = strategy.build_card()
        print(card)

        card_save = Prompt.ask(
            "Would you like to save your card?",
            choices=["Y", "N"],
        )

        if card_save == "Y":
            filename = Prompt.ask("Enter filename", default="creative_card")
            with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                f.write(card)
            print(f"Saved to {filename}.txt")
        else:
            continue_opt = Prompt.ask(
                "Create a new card?",
                choices=["Y", "N"],
                default="Y",
            )
            if continue_opt == "N":
                break


@app.command()
def main(
    terminal: bool = typer.Option(
        False,
        "--terminal",
        help="Run in the terminal instead of opening the web UI.",
    ),
) -> None:
    if terminal:
        run_terminal_loop()
    else:
        launch_web()


if __name__ == "__main__":
    print_banner()
    app()