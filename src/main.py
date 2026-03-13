import os
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent import Agent

BASE_DIR = Path(__file__).resolve().parent.parent

def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    parser = ArgumentParser()
    parser.add_argument("goal", help="High level user goal e.g. 'Help me compare the most common vector databases used today'")
    parser.add_argument("--verbose", action="store_true", help="Show detailed trace logs")
    args = parser.parse_args()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    agent = Agent(goal=args.goal, client=client, verbose=args.verbose)
    agent.run()

if __name__ == "__main__":
    main()