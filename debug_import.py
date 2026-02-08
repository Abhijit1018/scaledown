
import sys
import traceback

def main():
    try:
        print("Attempting imports...")
        import pulse.main
        print("Import successful!")
    except Exception:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print("Error occurred. Saved to error_log.txt")

if __name__ == "__main__":
    main()
