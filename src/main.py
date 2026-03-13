from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv

from agent import Agent
from client import OpenAIClient

BASE_DIR = Path(__file__).resolve().parent.parent

def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    parser = ArgumentParser()
    parser.add_argument("goal", help="High level user goal e.g. 'Help me compare the most common vector databases used today'")
    parser.add_argument("--verbose", action="store_true", help="Show detailed trace logs")
    args = parser.parse_args()

    client = OpenAIClient()
    agent = Agent(goal=args.goal, client=client, verbose=args.verbose)
    agent.run()

if __name__ == "__main__":
    main()