import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--data_ref', help='Data de Referência da ABT', default='2018-03-01')
args = parser.parse_args()
data_ref = pd.to_datetime(args.data_ref).date()

# mostra o ambiente que está sendo usado
os.system('python -c "import sys; print(sys.executable)"')

# executa o etl de predict
os.system('python src\data_prep\predict\etl.py --data_ref {data_ref}'.format(data_ref=data_ref))

# executa o predict
os.system('python src\ml\predict\predict.py')
