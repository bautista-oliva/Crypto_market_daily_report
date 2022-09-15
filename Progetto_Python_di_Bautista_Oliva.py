#importo le librerie e i moduli necessari
import requests
from pprint import pprint
import time
from datetime import datetime
import json
import pandas as pd
import os

#creo una classe in cui definisco tutte le funzioni
class Cryptos:
    #definisco i parametri per tutti gli oggetti e inserisco come parametro x che è il numero di cryptovalute
    # che verranno scaricate.
    def __init__(self,x=500):           # 'x' è il numero di cryptovlute che voglio scaricare
        self.url1 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest' #url della chiamata api
        self.params = {
            'start': '1',
            'limit': x,
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'ff93aebb-391b-44f6-877e-613c72797869'
        }

#funzione che effettua la chiamata api scaricando i dati
    def fetchCurrenciesData(self):  
        data =requests.get(url=self.url1, params=self.params, headers=self.headers).json()
        dati=data['data'] #dato che ricevo un dizionario con due valori di cui a noi interessa solo il primo, mi salvo direttamente solo quello **guardare prossimo commento
        return (dati)

    # In 'data' ricevo un dizionario con 2 chiavi: data e status.
    # Sotto la chiave 'data' trovo le informazioni riguardanti le cryptovalute.
    # Tali informazoini hanno la seguente struttura:
    # il valore di data è una lista contentente per ogni cryptovaluta un dizionario;
    # il dizionario di ogni cryptovaluta ha le seguenti chiavi: 'circulating_supply', 'cmc_rank', 'date_added',
    # 'id', 'last_updated', 'max_supply', 'name', 'num_market_pairs', 'platform', 'quote', 'self_reported_circulating_supply',
    # 'self_reported_market_cap', 'slug', 'symbol', 'tags' e 'total_supply'.
    # Il valore della chiave 'quote' è a sua volta un dizionario che per ogni valuta in 'num_market_pairs' fornisce un
    # dizonario con informazioni su prezzi e volumi (noi nei 'params' facciamo richiesta dei dati solo in USD)
    # il valore della chiave 'tags' continene una lista.


# funzione per trovare la cryptovaluta più scambiata in termini di USD
    def max_24h_volume(self, x=500): #x deve sempre essere minore o uguale all'x con cui si è definito l'oggetto di classe Cryptos
        if x>len(dati):              # se non lo è, viene trasformato nell x massimo possibile
            x=len(dati)
        best_24h_volume='none' #inizializzo una variabile in cui inserire il valore ricercato
        volumi=0 #questa variabile serve per calcolare il totale dei volumi di scambio utile a calcolare lo share della crypto più scambiata rispetto ai volumi totali
        currencies = dati #questo cambio di nomenclatura è dato dalla riscrittura del codice per permettere di copiare e incollare dalla vecchia versione
        for currency in currencies:
            if best_24h_volume == 'none' or currency['quote']['USD']['volume_24h'] > best_24h_volume['quote']['USD']['volume_24h']:
                best_24h_volume = currency
            volumi = volumi + currency['quote']['USD']['volume_24h']
        #pprint(f"La cryptovaluta più scambiata nelle ultime 24 ore è {best_24h_volume['name']}.")
        share_volumi = (best_24h_volume['quote']['USD']['volume_24h'] / volumi) * 100
        #pprint(
        #    f"I volumi di {best_24h_volume['name']} nelle ultime 24h rappresentano "
        #    f"il {share_volumi.__round__(2)} % dei volumi crypto delle prime {x} valute nelle ultime 24h")
        return best_24h_volume['name']

# funzione per ricavare la classifica dei 10 migliori e 10 peggiori titoli.
    def top_y(self, y=10):  # 'y' è il numero di crypto che voglio in classifica, che per consegna deve essere 10, ma ho voluto dare la possiblità di modificare tale numero
        if y>len(dati):              # se non lo è, viene trasformato nell x massimo possibile
            y=len(dati)
        #per semplificarmi la manipolazione dei dati me li trasformo in una lista di liste che poi trasformerò in dataframe. Lavorando con dizionari non sono riuscito a selezionare/ordinare i dati ricercati utilizzando meno risorse rispetto a questo metodo.
        crypto = []
        for i in range(len(dati)):
            crypto.append(i)
        for i in crypto:
            crypto[i] = [
                dati[i]['cmc_rank'], dati[i]['id'], dati[i]['name'],
                dati[i]['quote']['USD']['percent_change_24h']]
        # con l'operazione precedente l'intento è di ripulire i dati mantenendo solo alcune informazioni necessarie e
        # porre sullo stesso livello le voci in ['data'] e quelle in ['data']['quote']['USD'] in modo da semplificarne
        # l'utilizzo

        df_crypto = pd.DataFrame(crypto, columns=['ranking', 'id', 'name', '24h price variation']) #organizzo i dati in un dataframe (su cui potrò utilizzare la funzione .sort()
        # ora devo ordinare la tabella per '24h price variation'
        df_crypto_migliori = df_crypto.sort_values(by=['24h price variation'], axis=0, ascending=False)
        df_crypto_peggiori = df_crypto.sort_values(by='24h price variation', axis=0, ascending=True)
        s = y  # numero di crypto che voglio nella classifica
        #pprint(f'Le {s} crypto che hanno avuto la miglior variazione del prezzo nelle ultime 24 ore sono:')
        #pprint(df_crypto_migliori[0:s])
        #pprint(f'Le {s} crypto che hanno avuto la peggiore variazione del prezzo nelle ultime 24 ore sono:')
        #pprint(df_crypto_peggiori[0:s])
        top = df_crypto_migliori[0:s] #nel risultato voglio solo le prime y valute
        bottom = df_crypto_peggiori[0:s]
        #ora riorganizzo i dati in dizionari perchè poi mi servirà per creare il JSON
        top_names=top['name']
        top_prices_change=top['24h price variation']
        s=list(top['name'])
        t=list(top['24h price variation'])
        dict={}
        for i in range(len(s)):
            dict[s[i]]=t[i]
        top=dict
        s = list(bottom['name'])
        t = list(bottom['24h price variation'])
        dict2={}
        for i in range(len(s)):
            dict2[s[i]]=t[i]
        bottom=dict2
        return [top, bottom]

# funzione di data manipulation per poter semplificare lo svolgimento delle funzioni successive.
# converto i dati organizzati in dizionari in un dataframe
    def dati_preparati(self):
        dati_df = []
        for i in range(len(dati)):
            dati_df.append(i)
        for i in dati_df:
            dati_df[i] = [
                dati[i]['cmc_rank'],
                dati[i]['id'],
                dati[i]['name'],
                dati[i]['circulating_supply'],
                dati[i]['max_supply'],
                dati[i]['quote']['USD']['market_cap'],
                dati[i]['quote']['USD']['market_cap_dominance'],
                dati[i]['quote']['USD']['percent_change_1h'],
                dati[i]['quote']['USD']['percent_change_24h'],
                dati[i]['quote']['USD']['percent_change_30d'],
                dati[i]['quote']['USD']['percent_change_60d'],
                dati[i]['quote']['USD']['percent_change_7d'],
                dati[i]['quote']['USD']['percent_change_90d'],
                dati[i]['quote']['USD']['price'],
                dati[i]['quote']['USD']['volume_24h'],
                dati[i]['quote']['USD']['volume_change_24h'],
            ]
        # pprint(dati_df)
        dati_df = pd.DataFrame(dati_df, columns=['cmc_rank', 'id', 'name', 'circulating_supply',
                                                 'max_supply', 'market_cap', 'market_cap_dominance',
                                                 'percent_change_1h',
                                                 'percent_change_24h', 'percent_change_30d', 'percent_change_60d',
                                                 'percent_change_7d',
                                                 'percent_change_90d', 'price', 'volume_24h', 'volume_change_24h'])
        return dati_df

#funzione per ricavare quanto costi comprare una unità  di ognuna delle prime 20 cryptovalute
    def BuyTopS(self, s=20): #s è modificabile a piacimento purchè sia minore del numeoro di crypto di cui si sono scaricati i dati
        if s>len(dati):              # se non lo è, viene trasformato nell s massimo possibile
            s=len(dati)
        dati_df=report.dati_preparati()
        #pprint(f"Per acquistare una unità di ognuna delle prime 20 cryptovalute (per ordine di capitalizzazione"
        #       f" avresti dovuto spendere {dati_df[0:s]['price'].sum().round(2)}$")
        buy = dati_df[0:s]['price'].sum().round(2)
        return buy
#funzione per calcolare quanto costi acquistare una unità di ciascuna delle valute che hanno avuto volumi nelle ultime 24h maggiori di 76k USD
    def buy_volume_over_76M(self):
        dati_df = report.dati_preparati()
        res = 0 #inizializzo una varibile in cui vado a sommare i prezzi delle crypto che rispettano la condizione all'interno del ciclo for seguente
        for i in range(0, len(dati_df)):
            if dati_df['volume_24h'][i] > 76000000:
                res = res + dati_df['price'][i]
        #pprint(f"La quantità di denaro necessaria per acquistare una unità di tutte "
        #       f"le criptovalute il cui volume nelle ultime 24 ore sia superiore a 76.000.000$"
        #       f" è {round(res, 2)}$")
        return round(res, 2)

#funzione per calcolare la performance ottenuta in caso si fosse acquistata una unità di ciascuna delle prime 20 cryptovalute (in ordine di capitalizzazione)
    def performance_buying_top20(self):
        dati_df=report.dati_preparati()
        prezzi_ieri = 0 #inizializzo una variabile in cui andrò a sommare i prezzi di ieri (calcolati tramite prezzo di oggi e variazione nelle ultime 24h)
        prezzi_oggi = dati_df['price'][range(0, 20)].sum()
        for i in range(0, 20): #tramite iterazione calcolo e sommo i prezzi di ieri
            prezzi_ieri = prezzi_ieri + dati_df['price'][i] /(1+(dati_df['percent_change_24h'][i]/100))

        guadagno = (prezzi_oggi - prezzi_ieri) / prezzi_ieri
        guadagno_perc = guadagno * 100
        return guadagno_perc.round(2)

#chiamo le varie funzoni all'interno di un ciclo infinito che ogni volta che si esegue poi aspetta 24h prima di rieseguirsi
# e il cui risultato è la creazione di un JSON con i 5 risultati richiesti
while(1):
    risultato={}
    report = Cryptos(100)
    dati=report.fetchCurrenciesData()
    risultato['max_24h_volume']=report.max_24h_volume()
    risultato['top_10']=report.top_y()[0]
    risultato['bottom_10']=report.top_y()[1]
    risultato['buyTop20']=report.BuyTopS()
    risultato['buy_volume_over_76M']=report.buy_volume_over_76M()
    risultato['performance_buying_top20']=report.performance_buying_top20()
    cryptoreport=json.dumps(risultato)
    #f= open(append("report",date.today()),"w+")
    #pprint('report'+f'{datetime.date(datetime.today())}'+'.txt')
    #pprint(json.dumps(risultato))
    os.chdir(r'C:\Users\bauol\Desktop\Bautista\Start2impact\Blockchain')
    with open('report'+f'{datetime.date(datetime.today())}'+'.txt', 'w') as outfile:
        outfile.write(cryptoreport)
    #routine
    hours=24
    minutes = hours*60
    seconds = 60*minutes
    time.sleep(seconds)