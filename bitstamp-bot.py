#Multi bot 4.0  - autotuning portfolio percentage  implemented -order log and stat implemented-range trading implemented
#Lacks documentation ...please ask if you want to use this code by your own
# andrea.fantasia@gmail.com


import bitex
import time
       

def stampa_dic(dic):
    for kw in dic:
        print(kw, ":", dic[kw])
    print()



           
class multi_bot:    

   
    def __init__(self,pairs=['btceur','ltceur','etheur','xrpeur'],ranges={'btc':[3600,4600],'ltc':[25,35],'eth':[98,127,'xrp':[0.25,0.60]},trans_perc=0.01):

        def ratio():
            balance=retry(self.bot.balance()).json()
            eur_balance,crypto_balance=0,0
            for ticker in balance:
                if ticker=='eur_balance':
                    eur_balance+=eval(balance[ticker])
                else:
                    if ticker[4:]=='balance' and (ticker[:3]=='btc' or ticker[:3]=='ltc' or ticker[:3]=='xrp' or ticker[:3]=='eth'):
                        crypto_balance+=eval(balance[ticker])*eval(retry(self.bot.ticker(ticker[:3]+'eur')).json()['last'])
            return(eur_balance/crypto_balance)

        def calc_profit(init_balance={'eur':5000,'btc':0,'ltc':0,'eth':0,'xrp':0):
            balance=retry(self.bot.balance()).json()
            print('Initial balance')
            stampa_dic(init_balance)
            print('Actual balance')
            for w in balance:
                if w[4:]=='balance' and (w[:3]=='btc' or w[:3]=='eur' or w[:3]=='ltc' or w[:3]=='xrp' or w[:3]=='eth'):
                    print(w, balance[w])
            print()  
            hodl_gain=0
            for ticker in init_balance:
                if ticker=='eur':
                    hodl_gain+=init_balance['eur']
                else:
                    hodl_gain+=init_balance[ticker]*eval(retry(self.bot.ticker(ticker+'eur')).json()['last'])
            print(f'Hodl value {round(hodl_gain,2)} $')

            bot_gain=0
            for ticker in balance:
                if ticker=='eur_balance':
                    bot_gain+=eval(balance[ticker])
                else:
                    if ticker[4:]=='balance' and (ticker[:3]=='btc' or ticker[:3]=='ltc' or ticker[:3]=='xrp' or ticker[:3]=='eth'):
                        bot_gain+=eval(balance[ticker])*eval(retry(self.bot.ticker(ticker[:3]+'eur')).json()['last'])
            print(f'Bot value {round(bot_gain,2)} $')
            with open('bot.log','a') as f:
               f.write(f'{time.ctime()} Bot value {bot_gain} $  Hodl value {hodl_gain} $'+'\n')
            
            return({'hodl_gain':hodl_gain,'bot_gain':bot_gain})
       

        def flush(pair):
            open_orders=self.bot.private_query('v2/open_orders/'+pair+'/').json()
            for order in open_orders:
                cancel_order=self.bot.private_query('cancel_order/', params={'id': order['id']}).json()
                print('Orders flushed= ',cancel_order)
    
        def rebalance(pairs,fromticker):
            balance=self.bot.balance().json()
            tickers=set()
            for pair in pairs:
                tickers.add(pair[:3])
                tickers.add(pair[3:])
            total=eval(balance[fromticker+'_balance'])
            for ticker in tickers-{fromticker}:
                last_ex_price=eval(self.bot.ticker(ticker+fromticker).json()['last'])
                total+=eval(balance[ticker+'_balance'])*last_ex_price
            for ticker in tickers-{fromticker}:
                last_ex_price=eval(self.bot.ticker(ticker+fromticker).json()['last'])
                amount=eval(balance[ticker+'_balance'])*last_ex_price-total/len(tickers)
                if amount<0:
                    buy_order=bot.private_query(f'v2/buy/instant/{ticker+fromticker}/', params={'amount': round(-amount,8)})
                    print(buy_order)
                if amount>0:
                    sell_order=bot.private_query(f'v2/sell/instant/{ticker+fromticker}/', params={'amount': round(amount,8)})
                    print(sell_order)
                print(ticker,amount)
            
        def build_frozen_table(trans,pair):
            with open('frozen.'+pair,'r') as f:
                f=list(f)
                frozen_table=eval(f[1])
                last_trans=eval(f[0])
                
            trans.reverse() 
            for t in trans:
                if t['id']>last_trans:
                    frozen_table.append([t[pair[:3]+'_'+pair[3:]],eval(t[pair[:3]])])
                    with open('trans.log','a') as f:
                        f.write(pair+' '+str(t)+'\n')
                    last_trans=t['id']
            frozen_table.sort(reverse=True)
            """if pair=='xrpeur':
                print(frozen_table,'\n')"""
            
            flag=True
            while flag:
                    flag=False
                    i=0
                    while i<len(frozen_table)-1: 
                        if frozen_table[i][1]<0:
                            frozen_table[i+1][1]+=frozen_table[i][1]
                            frozen_table.remove(frozen_table[i])
                            i-=1
                            flag=True         
                        i+=1
                    """if flag and pair=='xrpeur' :
                       print(frozen_table)"""
            
            for t in frozen_table:
                if t[1]*t[0]<0.001:
                    frozen_table.remove(t)
                    #print('Removed ',t)"""
            """if True:
                print(frozen_table,'\n')"""
            with open('frozen.'+pair,'w') as f:
                f.write(str(last_trans)+'\n')
                f.write(str(frozen_table)+'\n')
                
            return frozen_table

        def new_order_pair(pair,from_price,frozen_table):
                        
            portfolio_perc=trans_perc/((ranges[pair][1]-ranges[pair][0])/(ranges[pair][1]+ranges[pair][0]))
                        
            balance=self.bot.balance().json()
            with open('order.log','a') as f:
               f.write(str(time.ctime()+' '+pair+' '+from_price)+'\n')
       
            
            #buy_order
            amount=round(portfolio_perc*eval(balance['eur_available'])/(len(pairs)*from_price),8)
            
          
            if pair=='xrpeur':
                buy_price=round((from_price)*(1-trans_perc),5)
            else:
                buy_price=round((from_price)*(1-trans_perc),2)
                
            if amount*buy_price>5:
                buyorder=self.bot.bid(pair,buy_price,amount).json()
                print(f'Limit buy order {pair} for total {amount*buy_price} {pair[3:]}')
                stampa_dic(buyorder)
            else:
                print(f'Insufficient funds for limit buy order {pair} for total {amount*buy_price} {pair[3:]}')
                       
                


            

            #sell_order
            amount_avail=0
            if pair=='xrpeur':
                sell_price=round((from_price)*(1+trans_perc),5)
            else:
                sell_price=round((from_price)*(1+trans_perc),2)
            for t in frozen_table:
                    if t[0]<sell_price*(1-0.005):
                        amount_avail+=t[1] 

            if amount_avail*sell_price<5:
                amount_avail=0
                
            while amount_avail*sell_price<5 and frozen_table!=[]:
                
                tail=frozen_table.pop()
                if pair=='xrpeur':
                    sell_price=round((tail[0])*(1+trans_perc),5)
                else:
                    sell_price=round((tail[0])*(1+trans_perc),2)
                
                amount_avail+=tail[1]
                
            print('Amount_available = ',amount_avail,' sell_price= ',sell_price)
            

                             
            if amount_avail>portfolio_perc*eval(balance[pair[:3]+'_available']):
           
                sellorder=self.bot.ask(pair,sell_price, round(eval(balance[pair[:3]+'_available'])*portfolio_perc,8)).json()
                print(f'Limit sell order {pair} at {sell_price} for total {amount_avail*portfolio_perc*round(sell_price,2)} {pair[3:]}')

            elif amount_avail/eval(balance[pair[:3]+'_available'])<portfolio_perc and amount_avail*sell_price>5:
                sellorder=self.bot.ask(pair, sell_price, round(amount_avail,8)).json()
                print(f'Limit sell order {pair} at {sell_price} for total {amount_avail*round(sell_price,2)} {pair[3:]}')

            else:
                print(f'Insufficient funds at {sell_price} for limit sell order {pair} for total {amount*round(sell_price,2)} {pair[3:]}')
                sellorder=''
                                
            
            stampa_dic(sellorder)
            #with open('bot.log','a') as f:
                #f.write(str(sellorder)+'\n')
                

     
        self.bot=bitex.Bitstamp(key_file='bot04.keys')                       
        print('Opening REST session with exchange')
        print('Starting bot for pair %s'%pairs)
        print()
        for pair in pairs:
            open_orders=self.bot.private_query('v2/open_orders/'+pair+'/').json()
            print(f'\n{pair}  open orders')
            if open_orders==[]:
                print('None!')
            else:
                for j in open_orders:
                    stampa_dic(j)
                    
            trans=self.bot.private_query('v2/user_transactions/%s/'%pair,params={'limit':1000}).json()
            if len(trans)>0:
                last_bot_price=trans[0][pair[:3]+'_'+pair[3:]]
                #print('Transactions for',pair)
                #for t in trans:
                    #stampa_dic(t)
            else:
                print('Rebalancing',pairs)
                rebalance(pairs,'eur')
                        
            print('Last bot price level for %s='%pair,last_bot_price)
            last_ex_price=eval(self.bot.ticker(pair).json()['last'])
            print('Last exchanged price for %s='%pair,last_ex_price)
            balance=self.bot.balance().json()
            print()
        for w in balance:
            if (w[4:]=='available' or w[4:]=='balance' or w[4:]=='reserved') and (w[:3]=='btc' or w[:3]=='eur' or w[:3]=='ltc' or w[:3]=='xrp' or w[:3]=='eth'):
                print(w, balance[w])
        print()
        calc_profit()    
        print('Starting bot ...')
        while True:
        
            for pair in pairs:
                time.sleep(1.5)
                try:
                    open_orders=retry(self.bot.private_query('v2/open_orders/'+pair+'/')).json()
                    bot_transactions=retry(self.bot.private_query('v2/user_transactions/%s/'%pair,params={'limit':1000})).json()
                    frozen_table=build_frozen_table(bot_transactions,pair)
                    last_bot_price=bot_transactions[0][pair[:3]+'_'+pair[3:]]
                    last_ex_price=eval(retry(self.bot.ticker(pair)).json()['last'])

                    #print(f'\n{time.ctime()}  Checking order status...last price {last_ex_price}\n')

                    if len(open_orders)==2:
                        range=[eval(open_orders[0]['price']), eval(open_orders[1]['price'])]
                        range.sort()
                        if range[0]>last_ex_price or last_ex_price>range[1]:
                                print('Range violation...flushing orders\n',open_orders[1]['price'],open_orders[0]['price'],last_ex_price)
                                flush(pair)
                                new_order_pair(pair,last_ex_price,frozen_table)
                                            
                    elif len(open_orders)==1:
                        print('Flushing unpaired order...')
                        flush(pair)
                        new_order_pair(pair,last_ex_price,frozen_table)
                        
                        
                    elif len(open_orders)==0:
                        print('Zero orders!')
                        new_order_pair(pair,last_ex_price,frozen_table)
                        
                    elif len(open_orders)>2:
                        print('Orders number violation...flushing orders')
                        flush(pair)
                        new_order_pair(pair,last_ex_price,frozen_table)
                except:
                    print('Connection error...retrying HTTP request')
             

multi_bot()


