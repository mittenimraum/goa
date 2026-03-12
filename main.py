import sys

from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py 'your goal'")
        return

if __name__ == "__main__":
    main()