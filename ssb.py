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

input = open('twss/data/vocab.pk')
vocabList = pickle.load(input)
input.close()
model = svm_load_model("twss/data/svm_model.pk")

try:
    input = open("heckle_list.pk")
    heckle_list = pickle.load(input)
    input.close()
except:
    heckle_list = []

cutoff = 0.75

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
        if str(recordId) in heckle_list:
            return
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
        today = datetime.datetime.utcnow() + datetime.timedelta(seconds=-60)
        now = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        qr = svc.query("select id, body, (select id, commentbody from feedcomments order by createddate asc) from collaborationgroupfeed WHERE LastModifiedDate > "+now)
        self.findJokes(qr)

    def heckle(self, itemid):
        a = { 'type': 'FeedComment',
            'FeedItemId': itemid,
            'CommentType': 'TextComment',
            'CommentBody': 'That\'s what she said! #twss' }
        sr = svc.create([a])

        if str(sr[sf.success]) == 'true':
            print "id " + str(sr[sf.id])
            heckle_list.append(itemid)
        else:
            print "error " + str(sr[sf.errors][sf.statusCode]) + ":" + str(sr[sf.errors][sf.message])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage is ssb.py <username> <password>"
    else:
        bot = SheSaidBot()
        bot.login(sys.argv[1], sys.argv[2])

        try:
            while 1:
                bot.query()
        except (KeyboardInterrupt):
            output = open("heckle_list.pk","wb")
            pickle.dump(heckle_list, output)
            output.close()
            sys.exit(0)
        except:
            output = open("heckle_list.pk","wb")
            pickle.dump(heckle_list, output)
            output.close()
            raise
