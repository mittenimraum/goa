import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent import Agent

BASE_DIR = Path(__file__).resolve().parent.parent

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py 'Help me compare the most common vector databases used today'")
        return

    load_dotenv(BASE_DIR / ".env")

    goal = sys.argv[1]
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    agent = Agent(goal, client)
    agent.run()

if __name__ == "__main__":
    main()