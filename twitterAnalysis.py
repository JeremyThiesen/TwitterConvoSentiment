import base64
import urllib
import urllib2
import simplejson
import pickle

searchTerm = '#spacex'
numResults = 100
search = searchTerm.replace('#','%23').replace('@','%40')


consumerKey = 'zfdLZ030IXZJnTwdYS2qxQ'
consumerSecret = 'i4zoliFhsnV1npPu7p7lcJeK59bvoe83F9RN71NHw'

bearerTokenCredentials = consumerKey + ':' + consumerSecret
base64TokenCredentials = base64.b64encode(bearerTokenCredentials)
data = 'grant_type=client_credentials'
url = 'https://api.twitter.com/oauth2/token'
req = urllib2.Request(url,data)


auth = 'Basic ' + base64TokenCredentials
req.add_header('Authorization', auth)
req.add_header('Content-Type','application/x-www-form-urlencoded;charset=UTF-8')

response = simplejson.load(urllib2.urlopen(req))
bearerToken = response['access_token']
pickle.dump(bearerToken,open('bearerToken.p','wb'))



tweetUrl = 'https://api.twitter.com/1.1/search/tweets.json?q=' + search
total = 0
positive = 0
neutral = 0
negative = 0
related = {'hashtags':{},'users':{}}

for i in range(numResults/100):
    if i == 0:
        tweetUrl = 'https://api.twitter.com/1.1/search/tweets.json?count=100&result_type=recent&q=' + search
    else:
        tweetUrl = 'https://api.twitter.com/1.1/search/tweets.json?count=100&result_type=recent&q='+search+'&max_id='+maxId

    req = urllib2.Request(tweetUrl)
    req.add_header('Authorization', 'Bearer ' + bearerToken)
    
    try:
        tweets = simplejson.load(urllib2.urlopen(req))
    except:
        print tweetUrl

    
    
    
    
    
    maxId = None
    for status in tweets['statuses']:
        maxId = status['id']
        total += 1
        
        url = 'http://text-processing.com/api/sentiment/'
        values = {'text': status['text']}
        try:
            data = urllib.urlencode(values)
        except Exception, e:
            print str(e)

        req = urllib2.Request(url, data)
        response = simplejson.load(urllib2.urlopen(req))
        #result = response.read()
        label = response['label']
        #print label
        if label == 'pos':
            pos = 2
            positive += 1
        elif label == 'neutral':
            pos = 1
            neutral += 1
        else:
            pos = 0
            negative += 1
        
        try:
            for hashtag in status['entities']['hashtags']:
                if hashtag['text'] not in related['hashtags']:
                    related['hashtags'][hashtag['text']] = [0,[0,0,0]]
                related['hashtags'][hashtag['text']][0] += 1
                related['hashtags'][hashtag['text']][1][pos] += 1
    
            for user in status['entities']['user_mentions']:
                if user['screen_name'] not in related['users']:
                    related['users'][user['screen_name']] = [0,[0,0,0]]
                related['users'][user['screen_name']][0] += 1
                related['users'][hashtag['text']][1][pos] += 1
                
        except Exception, e:
            continue
            #print str(e)

print 'Total'
print total
print 'Positive Sentiment Total'
print positive
print 'Neutral Sentiment Total'
print neutral
print 'Negative Sentiment Total'
print negative

hashList = []
for hashtag in related['hashtags']:
    hashList.append([hashtag,float(related['hashtags'][hashtag][0])/total,related['hashtags'][hashtag][1]])
hashList.sort(key=lambda x: x[1], reverse = True)
print 'Related Hashtags'

print 'Hashtag + = -'
for item in hashList:
    if item[1] > .25:
        print item[0],item[2][0],item[2][1],item[2][2]

userList = []
for user in related['users']:
    userList.append([user,float(related['users'][user][0])/total,related['hashtags'][hashtag][1]])
userList.sort(key=lambda x: x[1], reverse = True)
print 'Related Users'
print 'User + = -'
for item in userList:
    if item[1] > .25:
        print item[0],item[2][0],item[2][1],item[2][2]


