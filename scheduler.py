import os
import argparse
from tqdm import tqdm
import pandas as pd

safras = ['2018-03-01', '2018-04-01', '2018-05-01', '2018-06-01']

for safra in tqdm(safras):
    os.system('python run_predict.py --data_ref {data_ref}'.format(data_ref=safra))
