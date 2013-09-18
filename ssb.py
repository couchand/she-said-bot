# she said bot
# the first chatter bot

import os
import sys
import datetime
import pickle
from svmutil import *
from pprint import pprint
from StringIO import StringIO

sys.path.append(os.path.abspath("twss/"))
sys.path.append(os.path.abspath("beatbox/"))

import beatbox
import xmltramp
from processSentence import *

sf = beatbox._tPartnerNS
svc = beatbox.Client()
beatbox.gzipRequest=False

input = open('../twss/data/vocab.pk')
vocabList = pickle.load(input)
input.close()
model = svm_load_model("../twss/data/svm_model.pk")

cutoff = 0.7

def twss(sentence):
    x = processSentence(str(sentence), vocabList)
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    p_label, p_acc, p_val = svm_predict([1], [x], model, '-b 1')
    sys.stdout = old_stdout
    return p_val[0][1]

class SheSaidBot:
    def login(self, username, password):
        self.password = password
        loginResult = svc.login(username, password)
        print "welcome " + str(loginResult[sf.userInfo][sf.userFullName])

    def check(self, qr):
        for rec in qr[sf.records:]:
            for r in rec[4][sf.records:]:
                m = r[3]
                v = twss(m)
                if cutoff < v:
                    print '--'
                    print m
                    print 'That\'s what she said! (' + str(v) + ')'
                    self.create(str(rec[1]))

    def dumpQueryResult(self, qr):
        self.check(qr)

        if (str(qr[sf.done]) == 'false'):
            qr = svc.queryMore(str(qr[sf.queryLocator]))
            self.check(qr)

    def query(self):
        qr = svc.query("select id, createdby.name, (select id, commentbody from feedcomments) from collaborationgroupfeed WHERE ParentId = '0F9E00000004vXoKAI'")
        self.dumpQueryResult(qr)

    def create(self, itemid):
        a = { 'type': 'FeedComment',
            'FeedItemId': itemid,
            'CommentType': 'TextComment',
            'CommentBody': 'That\'s what she said! #twss' }
        sr = svc.create([a])

        if str(sr[sf.success]) == 'true':
            print "id " + str(sr[sf.id])
            self.__idToDelete = str(sr[sf.id])
        else:
            print "error " + str(sr[sf.errors][sf.statusCode]) + ":" + str(sr[sf.errors][sf.message])

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "usage is ssb.py <username> <password>"
    else:
        bot = SheSaidBot()
        bot.login(sys.argv[1], sys.argv[2])
        bot.query()
