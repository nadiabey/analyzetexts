import pandas as pd
import json

raw_texts = pd.read_csv('/Users/nadiabey/Documents/imessages.csv', delimiter=',')  # data!
raw_msg_ids = json.loads(open('msgids.txt', 'r').read())  # get phone numbers from txt file and convert to dict
texts = raw_texts[raw_texts['chat_identifier'] != raw_msg_ids['Nadia']]  # exclude my phone number
raw_emojis = json.loads(open('emoji-unicode.txt', 'r').read())  # emoji names and 5-digit codepoints
emojis = {}
for key, value in raw_emojis.items():
    v = r"\U000" + value
    emojis[key] = v.encode().decode('unicode-escape')
msg_ids = {}  # initialize dict with contact info and # of messages
for key, value in raw_msg_ids.items():
    if key == 'Nadia':  # skip!
        continue
    msg_ids[key] = {'contact': value, 'incoming': 0, 'outgoing': 0}
# imessage reactions
rxns = ['Loved “', 'Liked “', 'Emphasized “', 'Questioned “', 'Disliked “', 'Removed a', 'Laughed at']


def get_contact(iden: str):
    """take name of contact (person), pull info from dict and filter modify dataframe"""
    if type(msg_ids[iden]['contact']) is not list:
        df = texts[texts['chat_identifier'] == msg_ids[iden]['contact']]  # filter so it's only that contact
        return df
    else:
        df = texts[texts['chat_identifier'].isin(msg_ids[iden]['contact'])]
        return df


def incoming_messages(data):
    """messages sent by someone else"""
    return data[data['is_from_me'] == 0]


def outgoing_messages(data):
    """messages i sent"""
    return data[data['is_from_me'] == 1]


def emoji_count(data):
    """find messages that contain an emoji and sum up the times that emoji appears, excluding rxns"""
    e_c = {}
    df = data[~data.text.str.contains('|'.join(rxns), na=False)]
    for x in emojis.values():
        msgs = [item for item in df['text'] if x in str(item)]
        if msgs:
            num = sum([em.count(x) for em in msgs])
            e_c[x] = num
    return e_c


def median(values: list) -> int:
    """calculate median of a list of ints"""
    dex = len(values) // 2
    if len(values) % 2:
        return sorted(values)[dex]
    return sum(sorted(values)[dex - 1: dex + 1]) / 2


def double_text(data, name: str) -> str:
    """take dataframe of exchanges with one chat_id and count number of texts sent before receiving response"""
    counts = {1: [], 0: []}  # 1 is me, 0 is other recipient(s)
    prev = None
    count = 0
    for index, row in data.iterrows():
        if row['is_from_me'] == prev:  # if current sender matches stored value add to count
            count += 1
        else:
            if prev is not None:  # if different sender add to list and reset count
                counts[prev].append(count)
                count = 0
            prev = row['is_from_me']
            count += 1
    try:
        in_avg = round(sum(counts[0]) / len(counts[0]), 1)
    except ZeroDivisionError:
        in_avg = 0
    try:
        out_avg = round(sum(counts[1]) / len(counts[1]), 1)
    except ZeroDivisionError:
        out_avg = 0
    in_median = median(counts[0])
    out_median = median(counts[1])
    out_analysis = 'On average, you send ' + str(out_avg) + ' messages before ' + name + ' responds. (median: ' + str(
        out_median) + ')'
    in_analysis = 'On average, ' + name + ' sends ' + str(in_avg) + ' messages before you respond. (median: ' + str(
        in_median) + ')'
    return out_analysis + '\n' + in_analysis


def count_words(data) -> dict:
    """count unique words in message, excluding reactions"""
    df = data[~data.text.str.contains('|'.join(rxns), na=False)]  # omit rxns
    words = {}
    content = [x.split() for x in df['text'] if type(x) == str]
    for msg in content:
        for word in msg:
            if word.lower() not in words:
                words[word.lower()] = 0
            words[word.lower()] += 1
    return words


def reactions(data) -> dict:
    """times used imessage reactions"""
    rxns = {'Loved': [], 'Liked': [], 'Emphasized': [], 'Questioned': [], 'Disliked': [], 'Removed': [], 'Laughed': []}
    for msg in data['text']:
        try:
            if msg.startswith('Loved “'):
                rxns['Loved'].append(msg)
            elif msg.startswith('Liked “'):
                rxns['Liked'].append(msg)
            elif msg.startswith('Emphasized “'):
                rxns['Emphasized'].append(msg)
            elif msg.startswith('Questioned “'):
                rxns['Questioned'].append(msg)
            elif msg.startswith('Disliked “'):
                rxns['Questioned'].append(msg)
            elif msg.startswith('Removed a'):
                rxns['Removed'].append(msg)
            elif msg.startswith('Laughed at'):
                rxns['Laughed'].append(msg)
        except AttributeError:  # skip floats
            continue
    return rxns


def first_message(data) -> str:
    if data.empty:
        return 'no data'
    return data['message_date'].iloc[0]


if __name__ == '__main__':
    """loop through a dict containing a person's full contact name (full) and print analysis with their nickname/shortened name (short)""" 
    for full, short in d.items():
        person = get_contact(full)
        incoming = incoming_messages(person)
        outgoing = outgoing_messages(person)
        print(short)
        print('sent:', len(outgoing))
        print('received:',len(incoming))
        print('total:',str(len(outgoing) + len(incoming)))
        print('first incoming:', first_message(incoming))
        print('first outgoing:', first_message(outgoing))
        print('emojis sent:', emoji_count(outgoing))
        print('emojis received:', emoji_count(incoming))
        print('reactions sent:', reactions(outgoing))
        print('reactions received', reactions(incoming))
        print(double_text(person, short))
        print('\n')
