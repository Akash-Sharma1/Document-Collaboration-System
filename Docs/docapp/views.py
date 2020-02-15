from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe
import json
from .models import Commits, Pulls
from django.db import connection
from django.http import HttpResponseRedirect
import datetime
import hashlib


def index(request):
    return render(request, 'docapp/index.html', {})

def gotoeditpage(request,room_name,c_name,branch_name):
    q=Commits.objects.filter(Docid=room_name, branch=branch_name).all()
    q=q[len(q)-1]
    Document=q.Document
    return HttpResponseRedirect('/doc/'+c_name+'/'+room_name+'/'+branch_name+'/', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'name_json': mark_safe(json.dumps(c_name)),
        'branch_json': mark_safe(json.dumps(branch_name)),
        'para': Document
    })

def main(request, room_name,c_name,branch_name):
    q=Commits.objects.filter(Docid=room_name, branch=branch_name).all()
    
    qq=Commits.objects.filter(Docid=room_name, branch='master').all()
    #if no master create master
    if qq.count()==0:
        Document=''
        sha = hashlib.sha1(Document.encode())
        sha = sha.hexdigest()
        q=Commits(Docid=room_name,author=c_name,Document=Document,sha=sha,branch=branch_name)
        q.save()
    
    #if no current branch make a branch
    if branch_name!='master' and qq.count()>0 and q.count()==0:
        qq=qq[len(qq)-1]
        qq=Commits(Docid=qq.Docid,author=c_name,Document=qq.Document,sha=qq.sha,branch=branch_name)
        qq.save()
    
    q=Commits.objects.filter(Docid=room_name, branch=branch_name).all()
    q=q[len(q)-1]
    Document=q.Document
    return render(request, 'docapp/edit.html', {
            'room_name_json': mark_safe(json.dumps(room_name)),
            'name_json': mark_safe(json.dumps(c_name)),
            'branch_json': mark_safe(json.dumps(branch_name)),
            'para': Document
        })
             
def history(request, room_name,c_name):
    q=Commits.objects.filter(Docid=room_name).all()
    Document=[]
    q=q[::-1]
    for data in q:
        Document.append({
            'author': data.author,
            'timestamp': data.timestamp,
            'Document': data.Document,
            'id': data.id,
            'isdiff': data.isdiff,
            'branch': data.branch,
        })
    return render(request, 'docapp/history.html', {'arr':Document})


def pull_requests(request,room_name,c_name,branch_name):
    if request.method!='POST':
        if(branch_name!='master'):
            return gotoeditpage(request,room_name,c_name,branch_name)
        
        q=Pulls.objects.filter(Docid=room_name).all()
        
        if len(q)==0:
            return gotoeditpage(request,room_name,c_name,branch_name)
        
        Document=[]
        q=q[::-1]
        for data in q:
            Document.append({
                'id': data.id,
                'timestamp': data.timestamp,
                'Document': data.Document,
                'branch': data.branch,
            })
            
        return render(request, 'docapp/PRs.html', {
            'room_name_json': mark_safe(json.dumps(room_name)),
            'name_json': mark_safe(json.dumps(c_name)),
            'branch_json': mark_safe(json.dumps(branch_name)),
            'arr': Document
        })
    else:
        q1=Pulls.objects.filter(id=request.POST['num']).all()
        a=q1[0].Document
        q2=Commits.objects.filter(Docid=room_name, branch='master').all()
        b=q2[len(q2)-1].Document
        dic=lcs(a,b)
        a=textdiff(a,dic[0],dic[2])
        b=textdiff(b,dic[1],dic[3])
        return render(request,'docapp/TextDifferentiator.html',{
            'a':a,
            'b':b,
            'n1':q1[0].id,
            'n2':q2[0].id
        })

def pull(request,room_name,c_name,branch_name):
    return gotoeditpage(request,room_name,c_name,'master')

def push(request,room_name,c_name,branch_name):
    if branch_name=='master':
        return gotoeditpage(request,room_name,c_name,branch_name)
    
    q=Commits.objects.filter(Docid=room_name, branch=branch_name).all()
    q=q[len(q)-1]
    
    comp=Commits.objects.filter(Docid=room_name, branch='master').all()
    comp=comp[len(comp)-1]
    
    ##################Only checking duplicates#################
    if q.sha != comp.sha:
        newpr=Pulls.objects.filter(Docid=room_name, branch=branch_name).all().delete()
        newpr=Pulls(Docid=room_name, branch=branch_name,Document=q.Document)
        newpr.save()
    
    return HttpResponse("Pushed Your latest commits to the Pull Request Queue")
    return gotoeditpage(request,room_name,c_name,branch_name)
            
            

def saveit(request):
    if request.method=='POST':
        Docid=request.POST['docid']
        author=request.POST['author']
        Document=request.POST['Document']
        branch=request.POST['branch']
        
        sha = hashlib.sha1(Document.encode())
        sha = sha.hexdigest()
        
        q=Commits.objects.filter(Docid=Docid, branch=branch).all()
        
        if q.count()>0:
            q=q[len(q)-1]
            ###only checking sha duplicates
            if q.sha!=sha:
                q=Commits(Docid=Docid,author=author,Document=Document,sha=sha,branch=branch)
                q.save()
    
        string="/doc/"+author+'/'+Docid+"/"+ branch + '/'
        return HttpResponseRedirect(string)
    else:
        return HttpResponseRedirect("/")


def compare(request, room_name, c_name):
    if request.method != 'POST':
        q = Commits.objects.filter(Docid=room_name).all()
        Document = []
        q = q[::-1]
        for data in q:
            Document.append({
                'timestamp': data.timestamp,
                'Document': data.Document,
                'id': data.id,
                'branch': data.branch,
            })
        return render(request, 'docapp/Compare.html', {
            'room_name_json': mark_safe(json.dumps(room_name)),
            'name_json': mark_safe(json.dumps(c_name)),
            'arr': Document
        })
    else:
        q1 = Commits.objects.filter(id=request.POST['c1']).all()
        a = q1[0].Document
        q2 = Commits.objects.filter(id=request.POST['c2']).all()
        b = q2[0].Document
        dic = lcs(a, b)
        ans_a = change_tostring(a, dic[0], dic[2])
        ans_b = change_tostring(b, dic[1], dic[3])
        # ans contains { Document , Word matched 1 or not 0 , line is added 1 or deleted 2 or same 0 }
        return render(request, 'docapp/TextDifferentiator.html', {
            'info_a': ans_a,
            'info_b': ans_b,
            'n1': q1[0].id,
            'n2': q2[0].id
        })

# 0 nochange, 2 green, 1 red
def change_tostring(a, dic, rs):
    res = ""
    for i in range(len(a)):
        if a[i] != '\r':
            res+=str(rs[i])
    a = a.replace("\r\n", "\n")
    
    Doc=""
    line = 0
    linecolor=""
    for i in a:
        if line==0:
            Doc+=str(dic[line])
            line+=1
        if i=='\n':
            Doc+=str(dic[line])
            line+=1
            
    # Doc stores the lil0ne color weather the line is a +(1) or -(2) or null(0)
    # res stores the color of each character wheather is mathced or not 1 for matched 0 for not matched
    return {'Document': a,'wordinfo':res,'lineinfo':Doc}


def lcs(a, b):
    dp = [[0 for i in range(len(b) + 1)] for j in range(len(a) + 1)]
    resa = [0] * len(a)
    resb = [0] * len(b)
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            if a[i - 1] == b[j - 1]:
                dp[i][j] = max(dp[i][j], dp[i - 1][j - 1] + 1)
    ans = ""
    i = len(a)
    j = len(b)
    while dp[i][j] != 0:
        if i >= 0 and j >= 0 and dp[i][j] > dp[i - 1][j] and dp[i][j] != dp[i][j - 1]:
            resa[i - 1] = 1
            ans += a[i - 1]
            resb[j - 1] = 1
            i -= 1
            j -= 1
        if i >= 0 and dp[i][j] == dp[i - 1][j]:
            i -= 1
        if j >= 0 and dp[i][j] == dp[i][j - 1]:
            j -= 1
    ans = ans[::-1]

    diffA = []
    diffB = []
    i = 0
    j = 0
    lineA = 0
    lineB = 0

    while i < len(a) or j < len(b):
        wordsA = 0
        matchA = 0
        while (True):
            wordsA = 0
            matchA = 0
            while i < len(a) and a[i:i + 2] != "\r\n":
                wordsA += 1
                if resa[i] == 1:
                    matchA += 1
                i += 1
            if i<len(a):
                if resa[i] == 1:
                    matchA+=1
                if resa[i+1] == 1:
                    matchA+=1
                wordsA+=2
            i += 2
            lineA += 1
            if wordsA > 0 and matchA == 0:
                diffA.append('1')
            else:
                break

        wordsB = 0
        matchB = 0

        while (True):
            wordsB = 0
            matchB = 0
            while j < len(b) and b[j:j + 2] != "\r\n":
                wordsB += 1
                if resb[j] == 1:
                    matchB += 1
                j += 1
            if j<len(b):
                if resb[j] == 1:
                    matchB+=1
                if resb[j+1] == 1:
                    matchB+=1
                wordsB+=2
                
            j += 2
            lineB += 1
            if wordsB > 0 and matchB == 0:
                diffB.append('2')
            else:
                break

        if matchA == matchB and wordsA == matchA and wordsB == matchB and wordsA > 0:
            diffA.append('0')
            diffB.append('0')
            continue

        Blist = 1
        Alist = 1

        while matchA != matchB and i < len(a) and j < len(b):
            if matchA > matchB and j < len(b):
                while j < len(b) and b[j:j + 2] != "\r\n":
                    wordsA += 1
                    if resb[j] == 1:
                        matchB += 1
                    j += 1
                j += 2
                lineB += 1
                Blist += 1
            elif i < len(a):

                while i < len(a) and a[i:i + 2] != "\r\n":
                    wordsB += 1
                    if resa[i] == 1:
                        matchA += 1
                    i += 1
                i += 2
                lineA += 1
                Alist += 1

        for ind in range(Alist):
            diffA.append("1")
        for ind in range(Blist):
            diffB.append("2")
                
    dic = {0: diffA, 1: diffB, 2: resa, 3: resb}
    return dic
