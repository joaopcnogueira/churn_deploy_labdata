import dateutil
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

this_file = Path(__file__).absolute()
work_dir  = this_file.parent.parent.parent.parent.absolute()
data_dir  = work_dir.joinpath('data').absolute()

df_orders      = pd.read_csv(data_dir.joinpath('olist_orders_dataset.csv'), parse_dates=['order_approved_at'])
df_order_items = pd.read_csv(data_dir.joinpath('olist_order_items_dataset.csv'))
df_sellers     = pd.read_csv(data_dir.joinpath('olist_sellers_dataset.csv'))

parser = argparse.ArgumentParser()
parser.add_argument('--data_ref', help='Data de Referência da ABT', default='2018-01-01')
args = parser.parse_args()

data_ref = pd.to_datetime(args.data_ref).date()
data_inf = data_ref - dateutil.relativedelta.relativedelta(months=12)

df = (
    df_orders
    .query('order_status == "delivered"')
    .merge(df_order_items, on='order_id', how='inner')
    .query('order_approved_at >= "{data_inf}" & order_approved_at < "{data_sup}"'.format(data_inf=data_inf, data_sup=data_ref))
    .merge(df_sellers, on='seller_id', how='left')
    .filter(['order_id', 'order_item_id', 'product_id', 'price', 'freight_value', 'seller_id', 'seller_state', 'order_approved_at'])
)

# Construção das Features
# construimos a base ativa olhando 1 ano pra trás a partir da data de referência: 2018-01-01
# a base ativa é a base que com o histórico para construirmos a nossa variável target
df_features = (
    df
    .query('order_approved_at < "{data_ref}"'.format(data_ref=data_ref))
    .groupby('seller_id')
    .agg(uf                 = ('seller_state', 'first'),
         tot_orders_12m     = ('order_id', 'nunique'),
         tot_items_12m      = ('product_id', 'count'),
         tot_items_dist_12m = ('product_id', 'nunique'),
         receita_12m        = ('price', 'sum'),
         data_ult_vnd       = ('order_approved_at', 'max'))
    .reset_index()
    .assign(data_ref = lambda df: pd.to_datetime('{data_ref}'.format(data_ref=data_ref)))
    .assign(recencia = lambda df: (df['data_ref'] - df['data_ult_vnd']).dt.days)
    .filter(['data_ref', 'seller_id', 'uf', 'tot_orders_12m', 'tot_items_12m', 'tot_items_dist_12m', 'receita_12m', 'recencia'])
)

df_features.to_csv(data_dir.joinpath('abt_churn_scoring.csv'), index=False)
