import urllib.request
import http.cookiejar
import urllib.parse
import os.path
import json
from typecheck import *


_DEBUG=False

suffix={'python':'py','csharp':'cs','javascript':'js','ruby':'rb'}

class LeetCodeProcessor:
     def __init__(self,dir_for_download=None):
          print('initiating...')
          self.mydir = dir_for_download
          self.host = r'https://leetcode.com'
          self.succeed=set()
          self.failed={}
          self.skipped_count=0
          self.succeed_count=0
          self.to_save=None
          self.headers = {
          'Host': 'leetcode.com',
          'Connection': 'keep-alive',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
          'Referer': 'https://leetcode.com/submissions/',
          }

     def load(self,saved_data):
          if saved_data==None:
               return
          print('start loading...')
          if os.path.exists(saved_data):
               f=open(saved_data)
               self.last_record=f.readline().strip()
               f.close()
               print('load complete!')
          else:
               print('Your data will be saved at {}'.format(saved_data))
          
     def login(self,username=None,password=None):
          print('start logining...')
          cookie = http.cookiejar.CookieJar()
          handler = urllib.request.HTTPCookieProcessor(cookie)
          self.urlOpener = urllib.request.build_opener(handler)
          self.urlOpener.open(self.host)
          csrftoken = ""
          for ck in cookie:
              csrftoken = ck.value
          values = {'csrfmiddlewaretoken':csrftoken,'login':username,'password':password,'remember':'on'}
          values = urllib.parse.urlencode(values).encode()
          request = urllib.request.Request("https://leetcode.com/accounts/login/",values,headers=self.headers)
          self.urlOpener.open(request)
          print('login complete!')

     def request(self,process_once=100):
          print('start collecting data...')
          offset=0
          while True:
               page=self.urlOpener.open(urllib.request.Request("https://leetcode.com/api/submissions/?format=json&limit={}&offset={}".format(process_once,offset),headers=self.headers))
               data=json.loads(page.read().decode('utf-8').replace("\xc2\xa0",' '))
               for i in data["submissions_dump"]:
                    if i["status_display"]=="Accepted":
                         last_slash=i['url'].rfind('/',0,len(i['url'])-1)
                         if _DEBUG:
                              print('submission id: '+i['url'][last_slash+1:-1],'target: '+self.last_record)
                         if i['url'][last_slash+1:-1]==self.last_record:
                              data['has_next']=False
                              break
                         elif self.to_save==None:
                              self.to_save=i['url'][last_slash+1:-1]
                         try:
                              self.downloadCode(self.host+i['url'],i['title'],suffix[i['lang']] if i['lang'] in suffix else i['lang'])
                         except Exception as e:
                              print('when processing {}'.format(i['title']))
                              print(e)
                              if not (i['title'],i['lang']) in self.failed:
                                   self.failed[(i['title'],i['lang'])]=i['url']
               if data['has_next']==False:
                    break
               else:
                    offset+=process_once
          print('finish processing!')
          print('stat: succeeded {} files, failed {} files, skipped {} files'.format(self.succeed_count,len(self.failed),self.skipped_count))

     def downloadCode(self,codeadd,title,format):
          if (title,format) in self.succeed:
               self.skipped_count+=1
               return
          print('start processing {}'.format(title))
          if _DEBUG:
              print(title)
              print(codeadd)
          request = urllib.request.Request(codeadd,headers=self.headers)
          url = self.urlOpener.open(request)
          all = str(url.read())
          tar = "getLangDisplay: "
          index = all.find(tar,0)
          formatend=all.find(r',\n',index)
          start = all.find('submissionCode: ',formatend)
          finis = all.find(r",\n",start)
          code = all[start+18:finis-2]
          toCpp = {r'\\u000D':'\n',r'\\u000A':' ',r'\\u003B':';',r'\\u003C':'<',r'\\u003E':'>',r'\\u003D':'=',
          r'\\u0026':'&',r'\\u002D':'-',r'\\u0022':'"',r'\\u0009':'\t',r'\\u0027':"'",r'\\u005C':'\\'}
          for key in toCpp.keys():
              code = code.replace(key,toCpp[key])
          self.saveCode(code,title,format)

     def saveCode(self,code,title,format):
          if _DEBUG:
               print(code+"\n",title+'.'+format)
          if not os.path.exists(self.mydir + title +'.'+ format):
               f = open(self.mydir + title +'.' +format,'w')
               f.write(code)
               print('succeed '+ title)
               self.succeed_count+=1
          else:
               print('skipped '+ title)
               self.skipped_count+=1
          self.succeed.add((title,format))

     def retry(self):
          for i in self.failed:
               while True:
                    exitflag=False
                    ans=type_check((lambda x:x.upper(),lambda x:x=='Y' or x=='N'),hint="For {}, do you want to try again?('Y' or 'N')".format(i[0]),errormessage="Input must be 'Y' or 'N'")
                    if ans=='Y':
                         try:
                              self.downloadCode(self.host+self.failed[i],i[0],i[1])
                              break
                         except:
                              print('an error occurs when processing {}'.format(i[0]))
                              print(e)
                    else:
                         break
     def save(self):
          if hasattr(self,'saved_data') and self.to_save:
               f=open(self.saved_data,'w')
               f.write(self.to_save)
               f.close()
                                   


                                   

if __name__=="__main__":
     obj=LeetCodeProcessor('Your own directory to save the codes')
     obj.load('Your own file to save the progress to prevent re-download (can be None)')
     obj.login("Your own leetcode username","Your own password")
     obj.request()
     obj.retry()
     obj.save()









