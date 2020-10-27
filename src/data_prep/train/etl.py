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

# ABT DE TREINAMENTO
# data de referência: 2018-01-01
# pegaremos 18 meses, sendo os 12 primeiros meses para construir as features
# e os 6 meses restante para construir o target
data_ref = pd.to_datetime(args.data_ref).date()
data_inf = data_ref - dateutil.relativedelta.relativedelta(months=12)
data_sup = data_ref + dateutil.relativedelta.relativedelta(months=6)

df = (
    df_orders
    .query('order_status == "delivered"')
    .merge(df_order_items, on='order_id', how='inner')
    .query('order_approved_at >= "{data_inf}" & order_approved_at < "{data_sup}"'.format(data_inf=data_inf, data_sup=data_sup))
    .merge(df_sellers, on='seller_id', how='left')
    .filter(['order_id', 'order_item_id', 'product_id', 'price', 'freight_value', 'seller_id', 'seller_state', 'order_approved_at'])
)

# Construção das Features
# construimos a base ativa olhando 1 ano pra trás a partir da data de referência: 2018-01-01
# a base ativa é a base que com o histórico para construirmos a nossa variável target
df_base_ativa = (
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
)

# Construção do Target
df_target_horizonte = (
    df
    .query('order_approved_at >= "{data_ref}" & order_approved_at < "{data_sup}"'.format(data_ref=data_ref, data_sup=data_sup))
    .filter(['seller_id'])
    .drop_duplicates()
)

# Juntando as features com o target
df_abt_train = (
    df_base_ativa
    .merge(df_target_horizonte, how='left', on='seller_id', indicator=True)
    .assign(churn_6m = lambda df: np.where(df['_merge'] == "left_only", 1, 0))
    .filter(['data_ref', 'seller_id', 'uf', 'tot_orders_12m', 'tot_items_12m', 'tot_items_dist_12m', 'receita_12m', 'recencia', 'churn_6m'])
)


# ABT OUT OF TIME
data_ref_oot = data_ref + dateutil.relativedelta.relativedelta(months=1)
data_inf_oot = data_ref_oot - dateutil.relativedelta.relativedelta(months=12)
data_sup_oot = data_ref_oot + dateutil.relativedelta.relativedelta(months=6)

df = (
    df_orders
    .query('order_status == "delivered"')
    .merge(df_order_items, on='order_id', how='inner')
    .query('order_approved_at >= "{data_inf}" & order_approved_at < "{data_sup}"'.format(data_inf=data_inf_oot, data_sup=data_sup_oot))
    .merge(df_sellers, on='seller_id', how='left')
    .filter(['order_id', 'order_item_id', 'product_id', 'price', 'freight_value', 'seller_id', 'seller_state', 'order_approved_at'])
)

df_base_ativa = (
    df
    .query('order_approved_at < "{data_ref}"'.format(data_ref=data_ref_oot))
    .groupby('seller_id')
    .agg(uf                 = ('seller_state', 'first'),
         tot_orders_12m     = ('order_id', 'nunique'),
         tot_items_12m      = ('product_id', 'count'),
         tot_items_dist_12m = ('product_id', 'nunique'),
         receita_12m        = ('price', 'sum'),
         data_ult_vnd       = ('order_approved_at', 'max'))
    .reset_index()
    .assign(data_ref = lambda df: pd.to_datetime('{data_ref}'.format(data_ref=data_ref_oot)))
    .assign(recencia = lambda df: (df['data_ref'] - df['data_ult_vnd']).dt.days)
)

df_target_horizonte = (
    df
    .query('order_approved_at >= "{data_ref}" & order_approved_at < "{data_sup}"'.format(data_ref=data_ref_oot, data_sup=data_sup_oot))
    .filter(['seller_id'])
    .drop_duplicates()
)

df_abt_oot = (
    df_base_ativa
    .merge(df_target_horizonte, how='left', on='seller_id', indicator=True)
    .assign(churn_6m = lambda df: np.where(df['_merge'] == "left_only", 1, 0))
    .filter(['data_ref', 'seller_id', 'uf', 'tot_orders_12m', 'tot_items_12m', 'tot_items_dist_12m', 'receita_12m', 'recencia', 'churn_6m'])
)

# JUNTANDO A BASE DE TREINO E ABT
df_abt = pd.concat([df_abt_train, df_abt_oot])
df_abt.to_csv(data_dir.joinpath('abt_churn_train.csv'), index=False)
