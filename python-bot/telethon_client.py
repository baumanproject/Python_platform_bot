from telethon import TelegramClient, events, utils
from telethon_settings import words_to_catch, admin_ids
import pymongo
import traceback

from telethon.tl.functions.channels import GetParticipantsRequest

from telethon.tl.types import InputChannel
from telethon.tl.types import ChannelAdminLogEventsFilter

api_id = 104895
api_hash = "2c81b703744fc21830be77a3a4ebe138"
phone = '+79777576366'

client = TelegramClient('MessageHunter', api_id, api_hash).start()

@client.on(events.NewMessage())
def handler(event):
    mongoClient = pymongo.MongoClient('localhost', 27017, connect=False)
    db = mongoClient.telegram
    stats = db.statistic

    try:
        sender = event.get_sender()
        entity = event.message
        if sender == None:
            return
        chat = event.get_chat()

        # логика отображения статистики
        def extract_count(json):
            try:
                return int(json['messages_count'])
            except KeyError:
                return 0

        # если шлем запрос на статистику
        if str(event.to_id).startswith('PeerUser') and event.to_id.user_id in admin_ids:
            if event.text == 'stats':
                outStream = []
                docs = list(stats.find({}))
                docs.sort(key=extract_count, reverse=True)
                for i in range(100 if len(docs) > 100 else len(docs)):
                    name = (docs[i]['first_name'] if docs[i]['first_name'] != None else '') + ' ' + (docs[i]['last_name'] if docs[i]['last_name'] != None else '')
                    username = docs[i]['username'] if docs[i]['username'] != None else "No username"
                    inputString = "{:30s} {:30s} {:30s} {:25s}".format(username, str(name), str(docs[i]['chatname']), str(docs[i]['messages_count']))
                    print(inputString)

        if str(event.to_id).startswith('PeerChannel'):
            chat_id = str(event.to_id.channel_id)
        elif str(event.to_id).startswith('PeerUser'):
            chat_id = str(event.to_id.user_id)
        else:
            chat_id = str(event.to_id.chat_id)
        filter = ChannelAdminLogEventsFilter(True, False, False, False, True, True, True, True, True, True, True, True,
                                             True, True)

        chat_collection = db['%s' % chat.username]
        #print(chat_collection.count())
        str(event.to_id)
        if chat_collection.count() == 0 and not str(event.to_id).startswith('PeerUser'):
            print("LOAD CHAT")
            result = []
            offset = 0
            limit = 5000
            while_condition = True
            iterations = 0
            while while_condition:
                iterations +=1
                print(chat.access_hash)
                participants = client(GetParticipantsRequest(channel=InputChannel(int(chat_id), chat.access_hash), filter=filter, offset=offset, limit=limit, hash=0))
                result.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) > limit or iterations > 50:
                    while_condition = False
            json = []
            for user in result:
                json.append({'user_id' : str(user.id), 'username' : user.username})
            chat_collection.insert_many(json)

        from_id = str(event.from_id)
        onedoc = stats.find_one({'from_id' : from_id, 'chat_id' : chat_id})
        if onedoc != None:
            stats.update_one({'from_id' : from_id, 'chat_id' : chat_id},
                             {'$set' : {'messages_count' : str(int(onedoc['messages_count']) + 1)}})
        else:
            username = chat_collection.find_one({'user_id' : from_id})
            if username != None:
                username = username['username']
            stats.insert_one({'from_id': from_id, 'username': username,
                              'first_name': sender.first_name, 'last_name': sender.last_name,
                              'phone' : sender.phone, 'chat_id' : chat_id, 'chatname' : chat.username ,'messages_count' : '1'})

        for word in words_to_catch:
            if word in event.text:
                client.send_message('mentionsofdib', 'New mention\nUsername: %s\nName: %s\nChat: t.me/%s\nText:\n%s' %
                                    (sender.username, (str(sender.first_name) + ' ' + str(sender.last_name)), chat.username, event.text))

    except Exception as e:
        #print(chat.username)
        print(str(e))
        traceback.print_exc()
with client:
    client.run_until_disconnected()