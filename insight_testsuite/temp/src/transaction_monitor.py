#!/usr/bin/env python

# needed to support arguments given in run.sh, and to provide an exit in case
# of improperly formatted data
import sys
# needed to load json strings (could have been done with the ast.literal_eval)
import json


class purchase(object):
    def __init__(self, amount, timestamp, order):
        self.amount = amount
        self.timestamp = timestamp
        # this is a counter to keep track of the order of purchases so that when
        # sorting by time, we could also do a secondary sort by the order
        # such that order and timestamp will matter
        self.order = order


class user(object):
    # note you need to pass an ID val to instantiate
    def __init__(self, ID):
        self.ID = ID
        self.purchases = []
        self.friends = []

    def add_purchase(self, purchase):
        self.purchases.append(purchase)

    def befriend(self, friend):
        self.friends.append(friend)

    def unfriend(self, friend):
        self.friends.remove(friend)


def mean(values):
    return sum(values) / len(values)
# before values are passed to the function the lists must consist of floats


def sd(values):
    mv = mean(values)
    srs = sum([(v - mv)**2 for v in values])
    return (srs / len(values))**(.5)


# write into a list of the user's social network recursively
def get_social_network(person, net, levels, output):
    if levels >= 1:
        for friend in net[person].friends:
            if friend != person:
                if friend not in output:
                    output.append(friend)
                    get_social_network(net[friend].ID, net, levels - 1, output)


def update_network(ld, N):
    # this references a variable ouside of this function, as it is used
    # to keep track of the number of transactions, and will also
    # be referenced later when loading data from the api
    global order

    # check if user exists, if not add them (applies to all if statements)
    if ld['event_type'] == 'purchase':
        try:
            N[ld['id']].add_purchase(
                purchase(ld['amount'], ld['timestamp'], order))
            order = order + 1
        except:
            N.update({ld['id']: user(ld['id'])})
            N[ld['id']].add_purchase(
                purchase(ld['amount'], ld['timestamp'], order))
            order = order + 1

    if ld['event_type'] == 'befriend':
        try:
            N[ld['id1']].befriend(ld['id2'])
        except:
            N.update({ld['id1']: user(ld['id1'])})
            N[ld['id1']].befriend(ld['id2'])
        try:
            N[ld['id2']].befriend(ld['id1'])
        except:
            N.update({ld['id2']: user(ld['id2'])})
            N[ld['id2']].befriend(ld['id1'])

    # he except cases shouldn't happen in real life but leave them in for error checks
    if ld['event_type'] == 'unfriend':
        try:
            N[ld['id1']].unfriend(ld['id2'])
        except:
            N.update({ld['id1']: user(ld['id1'])})
            N[ld['id1']].unfriend(ld['id2'])
        try:
            N[ld['id2']].unfriend(ld['id1'])
        except:
            N.update({ld['id2']: user(ld['id2'])})

            N[ld['id2']].unfriend(ld['id1'])


# return the social network purchase properties for a specific user and number
# of degrees and transacitons
def network_mean_sd(usr, D, T, N):
    network_users = []
    get_social_network(usr, N, D, network_users)
    transactions = []
    for u in network_users:
        for p in N[u].purchases:
            transactions.append([p.timestamp, p.amount, p.order])

            # sort by two columns (timestamp and order)
    sorted_transactions = sorted(transactions, key=lambda x: (x[0], x[2]))

    # sort transactions by time in ascending order
    # get 2-T if less than T, otherwise return effectively infinite values if
    # not enough transactions... not a great way to handle this for now
    n_transactions = len(transactions)
    if n_transactions < T:
        if n_transactions >= 2:
            sorted_T_transactions = sorted_transactions[-n_transactions:]
        else:
            return 1e999, 1e999
    else:
        sorted_T_transactions = sorted_transactions[-T:]
    # force float values here to be used in mean/sd calculations
    values = [float(l[1]) for l in sorted_T_transactions]
    return mean(values), sd(values)


# empty dict to store key value pairs of user id (string) and value (user object)
N = {}

# get arguments to script from command line
past_data = sys.argv[1]
api_data = sys.argv[2]
flagged = sys.argv[3]


try:
    f_past = open(past_data, 'r')
except:
    print('could not open ' + past_data)
    sys.exit()


try:
    params = json.loads(f_past.readline())
    # number of friends
    D = int(params['D'])
    # number of transactions
    T = int(params['T'])
except:
    print('D/T parameters could not be read, stopping program')
    sys.exit()


# left this as a variable for the stdev thresholding
n_sd = 3.0

# initialize counter for order of transactions
order = 0
for line in f_past:
    try:
        ld = json.loads(line)
        update_network(ld, N)
    except:
        print('could not parse JSON string or update network')
        print('error in line below')
        print(line)
        print('moving on')
        pass

# this makes a blank new file each time the script is run
# overwriting the file each time may not be what would be wanted in reality
try:
    f_out = open(flagged, 'w')
    f_out.close()
except:
    print('could not open ' + flagged)
    sys.exit()

try:
    f_api = open(api_data, 'r')
except:
    print('could not open ' + api_data)
    sys.exit()

# since we made the blank file earlier, this will be appending lines to it
f_out = open(flagged, 'a')

for line in f_api:
    try:
        ld = json.loads(line)
    except:
        print('could not parse JSON string')
        print('error in line below')
        print(line)
        print('moving on')
        pass

    try:
        if ld['event_type'] == 'purchase':
            test_user = ld['id']
            test_amt = float(ld['amount'])
            net_mean, net_sd = network_mean_sd(test_user, D, T, N)
            if test_amt > net_mean + n_sd * net_sd:
                #                print(ld)
                #                print(net_mean, net_sd)
                #                print('hi')
                ld.update({'mean': '%.2f' % net_mean})
                ld.update({'sd': '%.2f' % net_sd})
                # print(ld)
                # preserve the desired formatting to pass test suite
                f_out.write(line[:-1] + ', ' + '\"mean\": \"' + '%.2f' %
                            net_mean + '\", \"sd\": \"' + '%.2f' % net_sd + '\"}\n')
#
    except:
        print('error getting network properties or writing the file')
        print(line)
        print('moving on')
        pass
    # if we are getting data from the api, we need to check if the transaction
    # is a purchase first, then if it is do the amount check
    # only afterwards do we want to update the database with that new
    # purchase. If it's not a purchase then we update the database anyways.
    try:
        update_network(ld, N)
    except:
        print('error updating network')
        print('error in line below')
        print(line)
        print('moving on')
        pass

f_out.close()
