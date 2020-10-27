from pathlib import Path

this_file = Path(__file__).absolute()
work_dir  = this_file.parent.parent.parent.absolute()
data_dir  = work_dir.joinpath('data').absolute()

f = open(data_dir.joinpath("abt_churn_scored.csv").absolute(), "x")
f.write("data_ref,seller_id,uf,tot_orders_12m,tot_items_12m,tot_items_dist_12m,receita_12m,recencia,Label,Score")
f.close()
