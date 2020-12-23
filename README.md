# Faça o Download do Projeto

Clique em `Code` e depois `Download Zip`.

# Instale o Anaconda

[Anaconda Download](https://www.anaconda.com/products/individual)

# Setup do Ambiente

`
conda create --name churn_deploy python=3.6.9
`

`
conda activate churn_deploy
`

`
pip install -r requirements.txt
`


# Baixar os Dados
Faça o download das bases de [dados da Olist no Kaggle](https://www.kaggle.com/olistbr/brazilian-ecommerce) e coloque-os na pasta `data`.

# Criar as bases de Treino e Test/Validação/Out of Time
No Windows:
`
python src\data_prep\train\etl.py --data_ref 2018-01-01
`

No Linux:
`
python src/data_prep/train/etl.py --data_ref 2018-01-01
`

# Treinando o Modelo (opcional)
Execute o notebook na pasta `notebooks/modeling.ipynb` para treinar o melhor modelo já selecionado em exercício na aula de PyCaret.
No final, você terá um modelo em formato `.pkl` salvo na pasta `models`.

# Criar tabela para receber os dados escorados
Execute o script `create_scored_table.py` para criar a tabela onde iremos guardar os dados com o score do modelo.

No Windows:
`
python src\utils\create_scored_table.py
`

No Linux:
`
python src/utils/create_scored_table.py
`

# Predict
Com o modelo treinado, executar o programa `run_predict.py` passando a data de referência da safra. Esse programa irá
executar em sequência os jobs de etl para criar os dados de predict, assim como o predict do modelo nos dados criados anteriormente.

No Windows:
`
python run_predict.py --data_ref 2018-03-01
`

No Linux:
`
python run_predict.py --data_ref 2018-03-01
`

# Executando Várias Safras
Aqui iremos simular o modelo em produção. Como esses dados são todos passados, não temos como schedular usando o `Windows Scheduler` ou `Crontab` de mês em mês. Por isso, o arquivo `scheduler.py` simula a passagem do tempo e execução do modelo a cada dia 01 do mês.

No Windows:
`
python scheduler.py
`

No Linux:
`
python scheduler.py
`

# Exibindo o Web App com Predição Online e Batch
Execute os seguintes comandos:

No Windows:
`
streamlit run app.py
`

No Linux:
`
streamlit run app.py
`
