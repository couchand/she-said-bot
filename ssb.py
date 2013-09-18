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

    def checkForJoke(self, recordId, message):
        v = twss(message)
        if cutoff < v:
            print '--'
            print message
            print 'That\'s what she said! (' + str(v) + ')'
            self.heckle(str(recordId))

    def checkPost(self, qr):
        for rec in qr[sf.records:]:
            comments = rec[4][sf.records:]
            if len(comments) == 0:
                self.checkForJoke(rec[1], rec[3])
            else:
                r = comments[-1]
                self.checkForJoke(rec[1], r[3])

    def findJokes(self, qr):
        self.checkPost(qr)

        if (str(qr[sf.done]) == 'false'):
            qr = svc.queryMore(str(qr[sf.queryLocator]))
            self.checkPost(qr)

    def query(self):
        qr = svc.query("select id, body, (select id, commentbody from feedcomments) from collaborationgroupfeed WHERE ParentId = '0F9E00000004vXoKAI'")
        self.findJokes(qr)

    def heckle(self, itemid):
        a = { 'type': 'FeedComment',
            'FeedItemId': itemid,
            'CommentType': 'TextComment',
            'CommentBody': 'That\'s what she said! #twss' }
        sr = svc.create([a])

        if str(sr[sf.success]) == 'true':
            print "id " + str(sr[sf.id])
        else:
            print "error " + str(sr[sf.errors][sf.statusCode]) + ":" + str(sr[sf.errors][sf.message])

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "usage is ssb.py <username> <password>"
    else:
        bot = SheSaidBot()
        bot.login(sys.argv[1], sys.argv[2])
        bot.query()
