import yfinance as yf
from pykrx import stock
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from io import BytesIO


def get_code_info():
    query_str_parms = {
        'locale': 'ko_KR',
        'mktId': 'ALL',
        'share': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01901'
        }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0'
        }
    r = requests.get('http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd', query_str_parms, headers=headers)
    form_data = {
        'code': r.content
        }
    r = requests.post('http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd', form_data, headers=headers)
    df = pd.read_excel(BytesIO(r.content)).rename(columns = {'단축코드':'Code','한글 종목약명':'Name'})
    return df

def get_adj_price(start_date, tickers) :
    df_prc = pd.DataFrame()
    for s in range(0, len(tickers)):
        cnt = round((datetime.today() - datetime.strptime(start_date, "%Y%m%d")).days * 25/30, 0)
        response = requests.get('https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count={}&requestType=0'.format(tickers[s],cnt))
        bs = BeautifulSoup(response.content, "html.parser")
        df_item = bs.select('item')
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = pd.DataFrame([], columns = columns, index = range(len(df_item)))
        for t in range(len(df_item)):
            df.iloc[t] = str(df_item[t]['data']).split('|')
            df['Date'].iloc[t] = datetime.strptime(df['Date'].iloc[t], "%Y%m%d")
            df['Close'].iloc[t] = int(df['Close'].iloc[t])
        df_temp = pd.DataFrame(df[['Date','Close']].set_index('Date'))
        df_temp.columns = [tickers[s]]
        df_prc_temp = df_temp
        df_prc = pd.concat([df_prc, df_prc_temp], axis=1)
    df_prc = df_prc.fillna(0).sort_index()
    return df_prc
