from SZlabeler.label_classifier import ExpRuleClassifier
import os
import time
location = os.path.abspath(os.path.dirname(__file__))
#print('hello, here is:',os.getcwd())

text1 = '清华大学深圳研究院电子通信硕士'
text2 = '深圳市罗湖区街道派出所民警'
text3 = '深圳市交通运输委员会福田交通运输局副局长'
text4 = '合肥炮兵学院炮兵指挥大学本科学士'

t0 = time.time()
label = ExpRuleClassifier()
print('Obj building Consuming:',time.time()-t0,'s')

print('\nSample Text:',text1)
t0 = time.time()
print(label.classify(text1))
print('Time Consuming:',time.time()-t0,'s')

print('\nSample Text:',text2)
t1 = time.time()
print(label.classify(text2))
print('Time Consuming:',time.time()-t1,'s')

print('\nSample Text:',text3)
t1 = time.time()
print(label.classify(text3))
print('Time Consuming:',time.time()-t1,'s')

print('\nSample Text:',text4)
t1 = time.time()
print(label.classify(text4))
print('Time Consuming:',time.time()-t1,'s')

# Testing on a mini dataset.
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
    '''
    if '深圳' in predict:
        predict.remove('深圳')'''
    if predict == []:
        toshow.append('0 '+resume)
    else:
        toshow.append('1 '+resume+'  '+str(predict))
        count += 1
print('Time Consuming:',time.time()-t0,'s')
print('Labeled resume:',count,'Total resume:',len(toshow))