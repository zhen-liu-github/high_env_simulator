import numpy as np
import pandas as pd


def load_data(data_path):
    data = np.load(data_path)
    return data


if __name__ == '__main__':
    data_path = 'simulator\models\dataset\data\sample_data.npy'
    data = load_data(data_path)[:, 1:]

    df = pd.DataFrame(data)
    df.columns = [
        'obs_x', 'obs_y', 'obs_vx', 'obs_vy', 'obs_hx', 'obs_hy', 'x', 'y',
        'vx', 'vy', 'hx', 'hy', 'episode_index', 'frame_index', 'gt_window_index'
    ]
    for name in ['episode_index', 'frame_index', 'gt_window_index']:
        df[name] = df[name].astype(int)
    sample_dict = {}
    for name, sample in df.groupby(['episode_index', 'frame_index']):
        sample = sample.sort_values('obs_x')
        if len(sample) not in list(sample_dict.keys()):
            sample_dict[len(sample)] = []
        sample_dict[len(sample)].append(sample)
    for key in sample_dict.keys():
        sample_dict[key] = pd.concat(sample_dict[key])
        sample_dict[key].to_csv('./simulator/models/dataset/data/'+str(key)+'.csv')