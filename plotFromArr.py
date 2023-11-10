import matplotlib.pyplot as plt
import csv
freq = []
mag = []
with open('./rlcFilter.csv','r') as file:
    print("File openned")
    reader = csv.reader(file)
    for row in reader:
        print(row)
        freq.append(row[0])
        mag.append(row[1])

plt.plot(freq,mag)
plt.show()