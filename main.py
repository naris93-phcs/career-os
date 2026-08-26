from src.database import create_database
from src.gui import run_gui


def main():
    create_database()
    run_gui()


if __name__ == "__main__":
    main()
