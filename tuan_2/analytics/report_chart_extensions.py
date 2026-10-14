"""Source-traceable matched-hour and submitted Week 1 reference figures."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'results/week2_analysis'
OUT = ROOT / 'results/week2_charts'
WEEK1 = ROOT.parent / 'tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051'
CITIES = ['HoChiMinh', 'HaNoi', 'DaNang']
CITY = {'HoChiMinh': 'TP. Hồ Chí Minh', 'HaNoi': 'Hà Nội', 'DaNang': 'Đà Nẵng'}
LABELS = {'week1': 'Báo cáo Tuần 1 (n=52)', 'default': 'Sinh viên Tiến Sơn Tuần 2 (n=9)', 'quyen': 'Sinh viên Ngọc Quyên Tuần 2 (n=19)'}
COLOURS = {'week1': '#64748B', 'default': '#2563EB', 'quyen': '#F59E0B'}
CATEGORIES = [('Good', 'Tốt', '#16A34A'), ('Moderate', 'Trung bình', '#EAB308'),
              ('Unhealthy for Sensitive Groups', 'Nhạy cảm', '#F97316'), ('Unhealthy', 'Không tốt', '#DC2626')]


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def matched_summary(rows, cities=CITIES):
    """Each common city-hour has one equal weight, independent of record count."""
    output = []
    metrics = ['us_aqi', 'pm2_5', 'pm10', 'temperature_2m', 'relative_humidity_2m']
    for city in cities:
        group = [row for row in rows if row['city'] == city]
        if not group:
            raise ValueError(f'No common observation hours for {city}')
        if len({r['timestamp_utc'] for r in group}) != len(group):
            raise ValueError(f'Common hours must be unique for {city}')
        item = {'city': city, 'common_hours': len(group),
                'son_records_in_common_hours': sum(int(r['son_samples']) for r in group),
                'quyen_records_in_common_hours': sum(int(r['quyen_samples']) for r in group)}
        for metric in metrics:
            for prefix in ('son', 'quyen', 'delta'):
                key = prefix + '_' + metric
                item[key] = statistics.mean(float(row[key]) for row in group)
        output.append(item)
    return output


def cent_value(amount):
    """Presentation rounding only; small signed zero displays as 0.00 USD."""
    rounded = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return abs(rounded) if rounded == 0 else rounded


def reference_comparison(week1_rows, week2_rows):
    import numpy as np
    groups = {'week1': week1_rows, **{p: [r for r in week2_rows if r['profile'] == p] for p in ('default', 'quyen')}}
    records = []
    for series, data in groups.items():
        for city in CITIES:
            group = [r for r in data if r['city'] == city]
            if not group:
                raise ValueError(f'Missing {series}/{city}')
            n = len(group); counts = Counter(r['aqi_category'] for r in group)
            for category, _, _ in CATEGORIES:
                records.append({'kind': 'aqi_category', 'city': city, 'series': series,
                    'student_label': LABELS[series], 'variable': category, 'n': n,
                    'count': counts[category], 'value': counts[category] / n * 100, 'unit': '%'})
            y = [float(r['pm2_5']) for r in group]
            for variable in ('temperature_2m', 'relative_humidity_2m', 'wind_speed_10m'):
                x = [float(r[variable]) for r in group]
                r = float(np.corrcoef(x, y)[0, 1]) if len(group) > 1 and len(set(x)) > 1 and len(set(y)) > 1 else None
                records.append({'kind': 'pearson_pm25', 'city': city, 'series': series,
                    'student_label': LABELS[series], 'variable': variable, 'n': n,
                    'count': '', 'value': r, 'unit': 'r'})
    return records


def plot_style():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 11,
        'axes.titlesize': 12, 'axes.labelsize': 11, 'axes.spines.top': False,
        'axes.spines.right': False, 'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.facecolor': 'white'})
    return plt


def matched_figure(summary):
    import numpy as np
    plt = plot_style(); fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.65))
    x = np.arange(len(summary)); width = .32
    for ax, metric, ylabel in zip(axes, ['us_aqi', 'pm2_5'], ['US AQI', 'PM2.5 (µg/m³)']):
        for index, (prefix, profile, label) in enumerate([('son', 'default', 'Sinh viên Tiến Sơn'), ('quyen', 'quyen', 'Sinh viên Ngọc Quyên')]):
            values = [r[prefix + '_' + metric] for r in summary]
            bars = ax.bar(x + (index - .5) * width, values, width, label=label, color=COLOURS[profile])
            ax.bar_label(bars, labels=[f'{v:.2f}' for v in values], padding=3, fontsize=10)
        ax.set_xticks(x, ['TP. HCM', 'Hà Nội', 'Đà Nẵng']); ax.set_ylabel(ylabel)
        maximum = max(r[p + '_' + metric] for r in summary for p in ['son', 'quyen'])
        ax.set_ylim(0, maximum * 1.2); ax.grid(axis='y', alpha=.18)
        ax.set_title('7 giờ quan trắc chung mỗi đô thị', fontsize=11)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .925), ncol=2, frameon=False, fontsize=11)
    return fig


def category_figure(records):
    plt = plot_style(); fig, axes = plt.subplots(1, 3, figsize=(10.5, 5.1))
    for ax, city in zip(axes, CITIES):
        bottom = [0., 0., 0.]
        for category, label, colour in CATEGORIES:
            values = [next(r['value'] for r in records if r['kind'] == 'aqi_category' and r['city'] == city and r['series'] == p and r['variable'] == category) for p in ('week1', 'default', 'quyen')]
            ax.bar(range(3), values, bottom=bottom, color=colour, label=label, width=.68)
            for i, value in enumerate(values):
                if value >= 6:
                    ax.text(i, bottom[i] + value / 2, f'{value:.1f}%', ha='center', va='center', fontsize=9)
                bottom[i] += value
        ax.set_xticks(range(3), ['Tuần 1\nn=52', 'Tiến Sơn\nTuần 2 n=9', 'Ngọc Quyên\nTuần 2 n=19'], fontsize=9)
        ax.set_ylim(0, 105); ax.set_title(CITY[city], fontsize=11); ax.grid(axis='y', alpha=.14)
    axes[0].set_ylabel('Tỷ lệ mẫu (%)')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .925), ncol=4, frameon=False, fontsize=10)
    return fig


def correlation_figure(records):
    import numpy as np
    plt = plot_style(); fig, axes = plt.subplots(1, 3, figsize=(10.5, 5.1))
    variables = ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']
    for ax, city in zip(axes, CITIES):
        values = np.array([[next(r['value'] for r in records if r['kind'] == 'pearson_pm25' and r['city'] == city and r['series'] == profile and r['variable'] == v) for v in variables] for profile in ('week1', 'default', 'quyen')])
        im=ax.imshow(values,vmin=-1,vmax=1,cmap='coolwarm',aspect='auto')
        for i in range(3):
            for j in range(3):ax.text(j,i,f'{values[i,j]:+.3f}',ha='center',va='center',fontsize=10,color='white' if abs(values[i,j])>.8 else 'black')
        ax.set_xticks(range(3), ['Nhiệt độ', 'Độ ẩm', 'Gió'], fontsize=10)
        ax.set_yticks(range(3),['Tuần 1 n=52','Tiến Sơn\nTuần 2 n=9','Ngọc Quyên\nTuần 2 n=19'],fontsize=9)
        ax.set_title(CITY[city], fontsize=11)
    fig.subplots_adjust(left=.1,right=.88,bottom=.18,top=.76,wspace=.66)
    colour_axis=fig.add_axes([.92,.18,.018,.58]);fig.colorbar(im,cax=colour_axis,label='Pearson r với PM2.5',ticks=[-1,-.5,0,.5,1])
    fig.fixed_layout=True
    return fig


def generate_extensions():
    plt = plot_style()
    paired_path = DATA / 'matched_account_hours.csv'
    raw1 = WEEK1 / 'raw_weather_aqi_records.csv'; raw2 = DATA / 'raw_week2_both_accounts.csv'
    summary = matched_summary(read_csv(paired_path))
    comparisons = reference_comparison(read_csv(raw1), read_csv(raw2))
    assert all(r['common_hours'] == 7 for r in summary)
    assert all(r['delta_us_aqi'] == r['delta_pm2_5'] == 0 for r in summary)
    for filename, data in [('matched_hour_summary.csv', summary), ('week1_week2_extended_comparison.csv', comparisons)]:
        with (DATA / filename).open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]), quoting=csv.QUOTE_ALL, lineterminator='\r\n')
            writer.writeheader(); writer.writerows(data)
    definitions = [
        ('09_matched_account_difference.png', 'AQI và PM2.5 trung bình tại các giờ quan trắc chung', matched_figure(summary), 'matched_account_hours.csv; matched_hour_summary.csv', summary, [paired_path]),
        ('19_week1_category_comparison.png', 'Phân bố cấp AQI trong báo cáo Tuần 1 và mẫu Tuần 2', category_figure(comparisons), 'week1_week2_extended_comparison.csv', [r for r in comparisons if r['kind'] == 'aqi_category'], [raw1, raw2]),
        ('20_week1_weather_correlation_comparison.png', 'Tương quan PM2.5 với khí tượng trong hai phạm vi tuần', correlation_figure(comparisons), 'week1_week2_extended_comparison.csv', [r for r in comparisons if r['kind'] == 'pearson_pm25'], [raw1, raw2])]
    manifest_path = OUT / 'chart_manifest.json'; manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for filename, title, fig, source, arrays, paths in definitions:
        fig.suptitle(title, fontsize=14, y=.99)
        fig.text(.02, .01, 'Nguồn: CSV đã lưu; các tập mẫu được phân tích theo phạm vi tương ứng', fontsize=8, color='#444444')
        if not getattr(fig,'fixed_layout',False):fig.tight_layout(rect=(0, .035, 1, .82))
        fig.savefig(OUT / filename, dpi=260, bbox_inches='tight', pad_inches=.16); plt.close(fig)
        entry = {'file': filename, 'title': title, 'source_csv': source,
                 'student_labels': {'default': 'Sinh viên Tiến Sơn', 'quyen': 'Sinh viên Ngọc Quyên'},
                 'account_colors': {'default': COLOURS['default'], 'quyen': COLOURS['quyen']},
                 'source_sha256': {p.relative_to(ROOT.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                 'plotted_data': arrays}
        existing = next((i for i, r in enumerate(manifest) if r['file'] == filename), None)
        if existing is None:manifest.append(entry)
        else:manifest[existing] = entry
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'matched_groups': 21, 'figures_updated': 3, 'new_derived_csv': 2, 'total_week2_figures': len(manifest)}))


if __name__ == '__main__':
    generate_extensions()
