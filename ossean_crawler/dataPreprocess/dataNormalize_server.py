#encoding:utf-8
import pymysql
from sklearn import preprocessing
conn =  pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ossean_production',
                       charset='utf8mb4')

import pandas as pd
from scipy.stats import zscore
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine


def normScore():
    engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/ossean_production?charset=utf8")
    sql = "select * from ossean_metric_zscore"
    df = pd.read_sql(sql, conn)

    df['score'] = zscore(df['score'])
    scaler = MinMaxScaler()
    df['score'] = scaler.fit_transform(df['score'].reshape(-1,1))
    df.to_sql(con=engine, name="ossean_metric_zscores", if_exists='append', index=False)

def normRanksScore():
    engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/ossean_production?charset=utf8")
    sql = "select * from ossean_ranks"
    df = pd.read_sql(sql, conn)

    scaler = MinMaxScaler()
    df['score'] = scaler.fit_transform(df['score'].reshape(-1,1))
    df.to_sql(con=engine, name="ossean_ranks_1", if_exists='append', index=False)


if __name__ == "__main__":
    # cal_active()
    # calPeople()
    # calScore()
    normRanksScore()
    # final()
    conn.close()




