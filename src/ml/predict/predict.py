import os
import joblib
import dateutil
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from pycaret.classification import load_model, predict_model

this_file = Path(__file__).absolute()
work_dir  = this_file.parent.parent.parent.parent.absolute()
data_dir  = work_dir.joinpath('data').absolute()
model_dir = work_dir.joinpath('models').absolute()

df = pd.read_csv(data_dir.joinpath('abt_churn_scoring.csv'))
model = load_model(str(model_dir.joinpath('model_churn')))

df_predictions = predict_model(estimator=model, data=df, probability_threshold=0.44)

abt_churn_scored = pd.read_csv(data_dir.joinpath('abt_churn_scored.csv'))

abt_churn_scored = pd.concat([abt_churn_scored, df_predictions])
abt_churn_scored.drop_duplicates(subset=['data_ref', 'seller_id'], inplace=True, keep='first')
abt_churn_scored.to_csv(data_dir.joinpath('abt_churn_scored.csv'), index=False)
