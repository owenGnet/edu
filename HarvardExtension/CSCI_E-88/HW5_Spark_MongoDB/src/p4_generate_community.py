# generate a list of user-ids in format of u##, zero-filled from the left as appropriate to total count
def get_userids(count):
    return ['u' + str.zfill('{}'.format(i), len(str(count))) for i in range(1, count+1)]

# generate 20 communityid values, spread across 5 distinct varieties, 4 "01", 4 "02" etc.
community_ids = ['community0{}'.format(i) for i in range(1,6) for j in range(4)]
# let's add an imbalance, so that final values for problem 4 query aren't all the same
# change the last value from community05 to community01
community_ids[-1] = 'community01'

uids = get_userids(20)
with open('DatasetCommunity', 'w') as f:
    for i,uid in enumerate(uids):
        f.write('{}\t{}\n'.format(uid, community_ids[i]))