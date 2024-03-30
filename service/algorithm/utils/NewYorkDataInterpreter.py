import csv
import time
import random
import pandas as pd

# New York original data is a CSV file of orders for an entire month. Extract data for a particular day and store it in the same structure as Chengdu.

# Generate a random ID
def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

if __name__ == '__main__':
    # 2016-01-02 00:00:00 timeStamp=1451664000
    # 2016-01-03 00:00:00 timeStamp=1451750400
    chars = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#-_.@')
    # print(random_string_generator(32, chars))
    with open('..\\..\\data\\NY_data\\yellow_tripdata_2016-01.csv', encoding='utf-8') as file:
        freader = csv.reader(file)
        data = []
        nsum = 0
        try:
            for row in freader:
                nsum += 1
        except UnicodeDecodeError:
            print('!')
            pass
        print(nsum)
        
        try:
            for row in freader:
                str = row[1]
                # Start processing if it's data from 01-02
                # Format: id, start timestamp, end timestamp, start longitude, start latitude, end longitude, end latitude
                if str[8] == '0' and str[9] == '1':
                    # Handle invalid data
                    if row[5] == '0':
                        continue
                    infoTuples = []
                    # Generate ID
                    tid = random_string_generator(32, chars)
                    infoTuples.append(tid)
                    # Convert timestamps
                    sTime = row[1]
                    timeArray = time.strptime(sTime, '%Y-%m-%d %H:%M:%S')
                    timeStamp = time.mktime(timeArray)
                    infoTuples.append(int(timeStamp))
                    eTime = row[2]
                    timeArray = time.strptime(eTime, '%Y-%m-%d %H:%M:%S')
                    timeStamp = time.mktime(timeArray)
                    infoTuples.append(int(timeStamp))
                    # Handle longitude and latitude data
                    infoTuples.append(f"{float(row[5]):.6f}")
                    infoTuples.append(f"{float(row[6]):.6f}")
                    infoTuples.append(f"{float(row[9]):.6f}")
                    infoTuples.append(f"{float(row[10]):.6f}")
                    # Store data
                    data.append(infoTuples)
        except UnicodeDecodeError:
            print('!')
            pass
        print('Sorting started')
        data.sort(key=lambda x: x[1])
        print('Storage started')
        df = pd.DataFrame(data)
        df.to_csv('order-2016-01-03', index=False, header=False)
