from datetime import datetime
time = datetime.now()
#date = time.date()
time = time.strftime('%Y-%m-%d %H:%M:%S')
print(time)