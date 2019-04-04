from flask import Flask, request, render_template,redirect,url_for
import telepot
import urllib3
import json
from web3 import Web3,HTTPProvider
from web3.middleware import geth_poa_middleware
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import requests
from emoji import emojize
import telepot.api
import pymongo

#import Exception
telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=6, timeout=30),
}

URL="http://57cb467b.ngrok.io"
money = emojize(":money_bag:",use_aliases=True)
OK = emojize(":white_check_mark:", use_aliases=True)
secret = "Anton"
global bot
bot = telepot.Bot('768245268:AAF6qK9C7AKGpB0_NG5QAVylSgG9XuooFAE')
markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Press to go to our website', url='https://www.dib.one')]])


def get_api_data():
    resp = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC,XRP,BCH&tsyms=USD&e=Kraken")
    data=resp.json()
    bitcoin_price = str(data["BTC"]["USD"])
    ethereum_price = str(data["ETH"]["USD"])
    litecoin_price = str(data["LTC"]["USD"])
    bitcash_price = str(data["BCH"]["USD"])
    ripple_price = str(data["XRP"]["USD"])
    str_BTC="*BTC*:  "  + bitcoin_price +" $"
    str_ETH="*ETH*: "   + ethereum_price + " $"
    str_XRP="*XRP*: "   + ripple_price + " $"
    str_BCH="*BCH*: "   + bitcash_price + " $"
    str_LTC="*LTC*: "   + litecoin_price + " $"
    all_= money + "`Current price`:\n" +  str_BTC +"\n" + str_ETH + "\n" + str_XRP + "\n" + str_BCH + "\n" + str_LTC
    return all_

app = Flask(__name__)
app.config["DEBUG"] = True
comments = []


client = pymongo.MongoClient('mongodb', 27017, connect=False)
db = client['telegram']


users = db.users.find({})
print('DETAILS')
for user in users:
    print(user)
details = db.details
#db.users.update_one({'telegram_id': 411954}, {'$set' : {'notifications' : 'on'}}, upsert=False)

'''@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://{}/HOOK'.format(URL), certificate=open('/etc/ssl/cert.pem', 'rb'))
    if s:
        #print(s)
        return "webhook setup ok"
    else:
        return "webhook setup failed"'''

@app.route('/{}'.format("oracle"),methods=["POST","GET"])
def oracle_request():
    client = pymongo.MongoClient('mongodb', 27017, connect=False)
    db = client['telegram']
    users = db['users']
    details = db.details

    if request.method == "GET":
       return("Status 2000! GET kamikadze!")
    update=request.get_json()
    print(update)
    #time.sleep(10)
    bool_seller = 1
    bool_buyer = 1
    print("INCOMING REQUEST FROM JS")
    if update["event_name"] == "Matching":
        #answer="Your " + update["type"]+ " was matched.\nParameters: \n"+"Margin: "+update["Margin"]+"\n"+"Premium: "+update["Premium"]+"\n"+"Strike price: "+update["Strike_price"]+"\n"+"End time: "+update["End_time"]+"\n"+ "Start time: "+update["Start_time"]+"\n"+"Block: "+update["Block"]
        answer = OK + " Your " + update["type"]+ " was matched " + OK + '\n'
        # Parameters: \n"+"Margin: "+update["Margin"]+"\n"+"Premium: "+update["Premium"]+"\n"+"Strike price: "+update["Strike_price"]+"\n"+"End time: "+update["End_time"]+"\n"+ "Start time: "+update["Start_time"]+"\n"+"Block: "+update["Block"]
    else:
        answer = OK + " Your " + update["type"]+ " was executed " + OK

    seller=update["seller_addr"]
    buyer=update["buyer_addr"]
    buyer_info = db.users.find_one({'public_key': buyer})
    seller_info = db.users.find_one({'public_key': seller})

    if seller_info is None:
        bool_seller = 0
        print("Nothing in db about seller")
    else:
        send_seller=seller_info['telegram_id']
        try:
            notifications = seller_info['notifications'] # этот блок кода - проверка включенных/отключенных нотификаций
        except:
            notifications = 'on'

        if notifications == 'off':
            pass
        else:
            while True:
                try:
                    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Details', callback_data='Details')]])
                    message = bot.sendMessage(send_seller, answer, reply_markup=markup)
                    db.details.insert_one({'user_id' : message['chat']['id'], 'message_id': message['message_id'], 'type':'call option',
                                        'Margin' : update["Margin"], 'Premium': update["Premium"], 'Strike_price': update["Strike_price"],
                                        'End_time': update["End_time"], 'Start_time': update["Start_time"], 'Block' : update["Block"]})
                    break
                except  telepot.exception.TelegramError as e:
                     raise e
                except  Exception as e:
                     break
                except telepot.exception.BotWasBlockedError:
                 #raise e
                     break

    if buyer_info is None:
       print("Nothing in db about buyer")
       bool_buyer = 0
    else:
        send_buyer = buyer_info['telegram_id']
        try:
            notifications = buyer_info['notifications']
        except:
            notifications = 'on'

        if notifications == 'off':      # этот блок кода - проверка включенных/отключенных нотификаций
            pass
        else:
            while True:
                try:
                    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Details', callback_data='Details')]])
                    message = bot.sendMessage(send_buyer, answer, reply_markup=markup)
                    details.insert_one({'user_id' : message['chat']['id'], 'message_id': message['message_id'], 'type':'call option',
                                        'Margin' : update["Margin"], 'Premium': update["Premium"], 'Strike_price': update["Strike_price"],
                                        'End_time': update["End_time"], 'Start_time': update["Start_time"], 'Block' : update["Block"]})
                    break
                except telepot.exception.TelegramError as e:
                    raise e
                except Exception as e:
                     break
                except telepot.exception.BotWasBlockedError:
                 #raise e
                    break
    if bool_buyer == 0 and bool_seller == 0 :
       return("130 Warning")
    return ('Status 200')



@app.route('/{}'.format("HOOK"), methods=["POST"])
def telegram_webhook():
    client = pymongo.MongoClient('mongodb', 27017, connect=False)
    db = client['telegram']
    update = request.get_json()

    if 'message' in update.keys(): #если пришло новое сообщение в бота
        user_info = db.users.find_one({'telegram_id': update["message"]["chat"]["id"]})
        try:
            notifications = user_info['notifications']
            if notifications == 'on':
                next_notifications = 'off'
            else:
                next_notifications = 'on'
        except:
            notifications = 'on'
            next_notifications = 'off'
        command = ""
        chat_id = update["message"]["chat"]["id"]

        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Add public key", callback_data = 'Add public key'), KeyboardButton(text="Our chat", callback_data="Our chat")],
                                                 [KeyboardButton(text="Description", callback_data='Notifications'), KeyboardButton(text='FAQ', callback_data='FAQ'), KeyboardButton(text=money+'Current price', callback_data='Current price')],
                                                 [KeyboardButton(text="Turn " + next_notifications + " notifications", callback_data = "Turn " + next_notifications + " notifications")]],
                                       one_time_keyboard= False, resize_keyboard = True)
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Press to go to our website',url = 'https://www.dib.one')]])
        markup2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Press to go to our Telegram chat',
                                                                              url = 'https://t.me/joinchat/El80Yg_jV0aPa-KOkzHKdw')]])
        for key in update["message"].keys():
            if key == 'text':
                command = update["message"]["text"]
            elif key=='photo':
                command = update["message"]["photo"]
                bot.sendMessage(chat_id, 'Photo is beautiful! Please open keyboard for commands!', reply_markup=keyboard)
                return 'OK'

        if command == '/start':
            bot.sendMessage(chat_id, 'Hello! Please, use keyboard for taking information.', reply_markup=keyboard)

        elif command == 'FAQ':
            str_1 = '1.    *What is DIB all about?*\n _     At DIB we liberate people from financial intermediaries by providing users a way to initiate, trade and settle derivative contracts in a fully peer-to-peer way. Our team exists out of world class mathematicians, programmers and hedge fund managers._\n\n'
            str_2 = '2.  *Will you do an ICO?*\n_        No. We think that a token, for example to pay fees, is not needed and will only reduce the user experience._\n\n'
            str_3 ='3.    *Will my tokens be safe?*\n _        We are strongly convinced that every user should have ownership of their own tokens at any time. We do not handle private keys or tokens of users at any time. Users use MetaMask to communicate with the blockchain._ \n\n'
            str_4 = '4.  *What is your mission?* \n _       At DIB, our mission is to develop open protocols for financial derivatives that can be used by anyone in the world. These protocols allow you and your neighbor to close derivative contracts that are enforced by the Ethereum blockchain._\n\n'
            str_5 = '5.   *Which derivatives will you offer?*\n _      In the short-term, we focus on option contracts and CFD’s. Later on, we will bring every investment banking product to the blockchain._'
            str_all=str_1+str_2+str_3+str_4+str_5
            print(str_all)
            bot.sendMessage(chat_id, text = str_all ,reply_markup = keyboard, parse_mode='Markdown')

        elif command == 'Our chat':
            bot.sendMessage(chat_id, text = 'Please, visit our chat!', parse_mode = 'Markdown', reply_markup = markup2)

        elif command == 'Add public key':
            bot.sendMessage(chat_id, text = "Please, add your public key to get notifications!" ,reply_markup = keyboard, parse_mode='Markdown')

        elif len(command)==42 and command[0]=='0'and command[1]=='x':

            users = db.users
            if users.find_one({'telegram_id' : update["message"]["from"]["id"]}) is None:
                users.insert_one({'telegram_id' : update["message"]["from"]["id"] , 'public_key' : command, 'notifications' : 'on'})
                bot.sendMessage(chat_id, text = "Now you will receive notifications about your positions! \n Your public key is {}".format(command) ,reply_markup = keyboard, parse_mode='Markdown')
            else:
                users.update_one({'telegram_id': update["message"]["from"]["id"]}, {'$set' : {'public_key' : command}}, upsert=False)
                bot.sendMessage(chat_id, text="Your public key was updated to {}".format(command),parse_mode='Markdown',reply_markup=keyboard )

        elif command[0:5] == "news:" and (chat_id == 308229218 or chat_id == 75422335):
             mess=command[5:len(command)]
             users=db.users

             for i in users.find():
                 try:
                     bot.sendMessage(int(i[0]),text=mess,parse_mode='Markdown',reply_markup=keyboard)
                 except telepot.exception.BotWasBlockedError:
                     pass

        elif command == money+'Current price':
            api_result = get_api_data()
            bot.sendMessage(chat_id, text=api_result,parse_mode='Markdown',reply_markup=keyboard )

        elif command == 'Hi':
            bot.sendMessage(chat_id, text="Hi,{}!".format(update['message']['from']['first_name']))

        elif command == 'Description':
            brief='As first in the world, DIB offers a platform on which you can initiate, trade and settle *financial products in a fully peer-to-peer way*! No banks, brokers or exchanges are needed, and at any time you remain the owner of your funds. This is a *true Fintech revolution*, and you are part of it! '
            bot.sendMessage(chat_id, text = brief, parse_mode ='Markdown', reply_markup = markup)

        elif command == 'Turn on notifications':
            db.users.update_one({'telegram_id': update["message"]["chat"]["id"]},
                                {'$set': {'notifications': "on"}}, upsert=False)
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="Add public key", callback_data='Add public key'),
                 KeyboardButton(text="Our chat", callback_data="Our chat")],
                [KeyboardButton(text="Description", callback_data='Notifications'),
                 KeyboardButton(text='FAQ', callback_data='FAQ'),
                 KeyboardButton(text=money + 'Current price', callback_data='Current price')],
                [KeyboardButton(text="Turn off notifications",
                                callback_data="Turn off notifications")]],
                                           one_time_keyboard=False, resize_keyboard=True)
            bot.sendMessage(chat_id=update["message"]["chat"]["id"], text="You will recieve notifications about your options.\n You can always turn it off.", reply_markup=keyboard)

        elif command == 'Turn off notifications':
            db.users.update_one({'telegram_id': update["message"]["chat"]["id"]},
                                {'$set': {'notifications': "off"}}, upsert=False)
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="Add public key", callback_data='Add public key'),
                 KeyboardButton(text="Our chat", callback_data="Our chat")],
                [KeyboardButton(text="Description", callback_data='Notifications'),
                 KeyboardButton(text='FAQ', callback_data='FAQ'),
                 KeyboardButton(text=money + 'Current price', callback_data='Current price')],
                [KeyboardButton(text="Turn on notifications",
                                callback_data="Turn on notifications")]],
                                           one_time_keyboard=False, resize_keyboard=True)
            bot.sendMessage(chat_id=update["message"]["chat"]["id"], text="You will not recieve notifications about your options.\n You can always turn it back.", reply_markup=keyboard)

        else:
            try:
                bot.sendMessage(chat_id,text = 'Try to use commands and buttons on inline keyboard',reply_markup = keyboard)
            except:
                print('sorry')

    elif 'callback_query' in update.keys(): #если пришла коллбэк-команда

        if update['callback_query']['data'] == 'Details':
            details = db.details.find_one({'user_id': update['callback_query']['from']['id'], 'message_id': update['callback_query']['message']['message_id']})
            print(details)
            if details is not None:
                answer = OK + " Your " + details["type"]+ " was matched " + OK + "\n*Parameters:* \n"+"`Margin:       `" \
                    ""+details["Margin"]+"\n"+"`Premium:      `"+details["Premium"]+"\n"+"`Strike price: `" \
                    ""+details["Strike_price"]+"\n"+"`End time:     `"+details["End_time"]+"\n"+ "`Start time:   `" \
                ""+details["Start_time"]+"\n"+"`Block:        `"+details["Block"]

                markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Hide details', callback_data='Hide details')]])
                bot.editMessageText(msg_identifier=(update['callback_query']['message']['chat']['id'], update['callback_query']['message']['message_id']), text=answer, reply_markup=markup, parse_mode='Markdown')

        elif update['callback_query']['data'] == 'Hide details':
            answer = (" ").join(update['callback_query']['message']['text'].split()[:7])
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Details', callback_data='Details')]])
            bot.editMessageText(msg_identifier=(update['callback_query']['message']['chat']['id'], update['callback_query']['message']['message_id']), text=answer, reply_markup=markup)

        elif update['callback_query']['data'] == 'Turn on notifications':
            db.users.update_one({'telegram_id': update['callback_query']["message"]["chat"]["id"]},
                                {'$set': {'notifications': "on"}}, upsert=False)
            bot.sendMessage(chat_id=update['callback_query']["message"]["chat"]["id"], text="You will recieve notifications about your options.\n You can always turn it off.")

        elif update['callback_query']['data'] == 'Turn off notifications':
            db.users.update_one({'telegram_id': update['callback_query']["message"]["chat"]["id"]},
                                {'$set': {'notifications': "off"}}, upsert=False)
            bot.sendMessage(chat_id=update['callback_query']["message"]["chat"]["id"], text="You will not recieve notifications about your options.\n You can always turn it back.")
    return 'OK'


def handle_event(event):
    print(event)


def log_loop(event_filter, poll_interval,user_key):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
            info(event,user_key)
        time.sleep(poll_interval)

def info(event,user_key):
    if(event['data'].find(user_key)!=-1):
        if(event['address']=='0x043cD5dC050E65879939d3e2adc73289143d163C'):
            #print("CHECKING!!!     "+str(event['topics'][0]))
            #print(str(bytes.fromhex(match_event)))
            if(str(event['topics'][0]) == str(bytes.fromhex(match_event))):
                #send to data base
                hash_ = event['data'][130:]
                hash_="0x"+hash_
                print(hash_)
                mycontract=w3.eth.contract(abi=json.load(open('abi_put.json')),address='0x043cD5dC050E65879939d3e2adc73289143d163C')
                result=mycontract.functions.getOption(hash_).call()
                print(result)
        if(event['address']=='0xd3f87d3d1F690679F8c6956214a129458137BAbf'):
            #print("CHECKING!!!     "+str(event['topics'][0]))
            #print(str(bytes.fromhex(match_event)))
            if(str(event['topics'][0]) == str(bytes.fromhex(match_event))):
                #send to data base
                hash_ = event['data'][130:]
                hash_="0x"+hash_
                #print(hash_)
                mycontract=w3.eth.contract(abi=json.load(open('abi_call.json')),address='0xd3f87d3d1F690679F8c6956214a129458137BAbf')
                result=mycontract.functions.getOption(hash_).call()
                #print(result)

def run_time_current_price(current):
    resp = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,EUR")
    data=resp.json()
    b1=str(data["BTC"]["USD"])
    e1=str(data["ETH"]["USD"])
