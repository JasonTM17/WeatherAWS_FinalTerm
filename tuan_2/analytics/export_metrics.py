"""Export analytical queries through the Python AWS SDK."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from athena_export import main
if __name__ == '__main__':
    main(['--output', str(ROOT / 'results' / 'athena_queries'), *sys.argv[1:]])
