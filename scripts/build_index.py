import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieve.playbook_index import build_index

if __name__ == "__main__":
    print(f"Indexed {len(build_index())} whole handbook pages")
