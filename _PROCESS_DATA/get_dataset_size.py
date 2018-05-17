import pandas as pd

# danno errore:
# 2, 36, 39, 41
# users = [1, 6, 8, 9, 10, 11, 12, 16, 19, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 37, 38, 43]
users = [41]
for user in users:
    df = pd.read_csv("csv/user"+str(user)+"/c-wlan.csv", index_col=0)
    aa = dict()
    for item in df['ssid']:
        for x in str(item).split(";"):
            val = x.replace("'","").replace(" ","")
            if val in aa:
                aa[val] = aa[val]+1
            else:
                aa[val] = 0
    new_aa = [k for k in aa.keys() if aa[k] > 20]
    print("user: {0}, size: {1}, new_size: {2}".format(user, str(len(aa)), str(len(new_aa))))

# ERRORE: 41, 38
# users = [2, 36, 39, 1, 6, 8, 9, 10, 11, 12, 16, 19, 20, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 37, 43]
for user in users:
    print("user: %s" % user)
    df = pd.read_csv("csv/user"+str(user)+"/c-cell.csv", index_col=0)
    bb = set([str(_).replace("'",'') for _ in df['bid'].values])
    print("set size: %d" % len(bb))

    aa = dict()
    for _ in df['bid'].values:
        if _ in aa.keys():
            aa[_] = aa[_] + 1
        else:
            aa[_] = 1
    for t in [2, 10, 20]:
        print("t: %d --> %d" % (t, len([x for x in aa.keys() if aa[x] > t])))
