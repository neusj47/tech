from _load import *
from more_itertools import locate
import matplotlib.pyplot as plt
import matplotlib.dates as _mdates

start_date = '20220101'
tickers = ['010660','005930','011170','011780','055550']

df_code = get_code_info()
df_prc = get_adj_price(start_date, tickers)


MACD_oscilator = (df_prc.ewm(span=12).mean() - df_prc.ewm(span=26).mean()) - (df_prc.ewm(span=12).mean() - df_prc.ewm(span=26).mean()).ewm(span=9).mean()
MACD_sign = (df_prc.ewm(span=12).mean() - df_prc.ewm(span=26).mean()) > (df_prc.ewm(span=12).mean() - df_prc.ewm(span=26).mean()).ewm(span=9).mean()

MACD_temp = pd.DataFrame(MACD_sign.iloc[len(MACD_sign)-1])
MACD_temp.columns = ['tgt']
cnt = list(locate(MACD_temp['tgt'].tolist(), lambda x: x == True))
tgt_list = []
for i in range(0, len(cnt)) :
    tgt_list.append(MACD_sign.columns[cnt[i]])

fig, axes = plt.subplots(1, 3)
fig.set_size_inches((15, 5))
plt.subplots_adjust(wspace = 0.1, hspace = 0.1)
for s in range(0,3) :
    Code = tgt_list[s]
    name = df_code[df_code.Code == Code]['영문 종목명'].iloc[0][0:20]
    prc = df_prc[Code]
    temp = MACD_sign[Code]
    buy_start = ~temp & temp.shift(-1)
    buy_start = list(buy_start[buy_start].index)
    buy_end = (~temp & temp.shift(1)).shift(-1).fillna(False)
    buy_end = list(buy_end[buy_end].index)
    if buy_end and buy_start[0] > buy_end[0]:
        buy_start.insert(0, temp.index[0])
    if not buy_end or buy_start[-1] > buy_end[-1]:
        buy_end.append(temp.index[-1])

    data = []
    for i, _ in enumerate(buy_start):
        data.append((Code, buy_start[i], buy_end[i]))
    df_buy = pd.DataFrame(data=data, columns=('Code', 'start', 'end'))

    axes[s].plot(prc, lw=1.5, label=Code + ':' + name, color='#348dc1')
    # axes[0, 0].legend(loc="upper left")
    axes[s].set_title(Code + ':' + name, fontsize = 12)
    highlight = 'black' if False else 'red'
    for _, row in df_buy.iterrows():
        axes[s].axvspan(*_mdates.datestr2num([str(row['start']), str(row['end'])]), color=highlight, alpha=.1, hatch='///')
    # fig.autofmt_xdate()
    plt.subplots_adjust(hspace=0, bottom=0, top=1)
    fig.tight_layout()
    axes[s].spines['top'].set_visible(False)
    axes[s].spines['right'].set_visible(False)
    axes[s].spines['bottom'].set_visible(False)
    axes[s].spines['left'].set_visible(False)


