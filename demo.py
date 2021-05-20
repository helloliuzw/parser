from SZlabeler.label_classifier import *
import os
import time
location = os.path.abspath(os.path.dirname(__file__))
#print('hello, here is:',os.getcwd())

text1 = '清华大学深圳研究院电子通信硕士'
text2 = '深圳市罗湖区街道派出所民警'
text3 = '深圳市交通运输委员会福田交通运输局副局长'
text4 = '深圳市 无线电 管理 办公室 业务 处处长'

t0 = time.time()
label = ExpRuleClassifier()
print('Obj building Consuming:',time.time()-t0,'s')

def testclf(s):
    print('\nSample Text:',s)
    t0 = time.time()
    print(label.classify(s))
    print('Time Consuming:',time.time()-t0,'s')
    
testclf(text1)
testclf(text2)
testclf(text3)
testclf(text4)

# Testing on a mini dataset.
'''
f = open(location+'/data/final_version.txt','r',encoding='utf-8')
data = f.readlines()
f.close()
data = [item.strip().split()[1] for item in data if ' ' in item]

clf = ExpRuleClassifier()
toshow = []
count = 0
print('\nTesting on a mini dataset.')
t0 = time.time()
for resume in data:
    res_dict = clf.classify(resume)
    predict = [label for (label,value) in res_dict.items() if value==True]
    if predict == []:
        toshow.append('0 '+resume)
    else:
        toshow.append('1 '+resume+'  '+str(predict))
        count += 1
print('Time Consuming:',time.time()-t0,'s')
print('Labeled resume:',count,'Total resume:',len(toshow))
'''