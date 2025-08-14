import sys
from .ui import TaskAgentApp

def main():
    app = TaskAgentApp(sys.argv)
    app.run()


if __name__ == "__main__":
    main()
