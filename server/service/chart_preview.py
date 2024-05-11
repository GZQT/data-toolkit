import io

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates as mdates

from dto.generator import PreviewImageRequest
from service.line_chart_generator import fill_data


def preview_line_chart(data, request: PreviewImageRequest):
    np_datum = np.array(data['data'])
    df = pd.DataFrame({'time': data['time'], 'data': np_datum})

    df.set_index('time', inplace=True)
    plt.figure(figsize=(10, 5))
    resampled = df.resample(request.chart_time_range).mean()
    resampled = fill_data(request.chart_fill, resampled)
    plt.plot(resampled.index, resampled['data'], label='平均值', marker='', linewidth=1)
    date_format = mdates.DateFormatter('%Y%m%d')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.title(request.chart_name)
    plt.xlabel(request.chart_x_label)
    plt.ylabel(request.chart_y_label)
    plt.legend()
    plt.grid(request.chart_show_grid)
    rotation = request.chart_x_rotation
    if rotation < 0:
        plt.xticks(rotation=rotation, ha='left')
    elif rotation > 0:
        plt.xticks(rotation=rotation, ha='right')
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return buffer
