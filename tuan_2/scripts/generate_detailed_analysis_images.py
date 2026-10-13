"""Generate the four data charts from the saved CSVs."""
from pathlib import Path
import sys
import shutil
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analytics'))
import generate_charts
if __name__ == '__main__':
    for function in (generate_charts.plot_city_comparison, generate_charts.plot_hourly_trend,
                     generate_charts.plot_category_distribution, generate_charts.plot_correlation):
        function()
    for source in Path(generate_charts.CHARTS_DIR).glob('*.png'):
        if source.name.startswith(('01_', '02_', '03_', '04_')):
            shutil.copyfile(source, ROOT / 'docs' / (source.stem + '_detailed.png'))
