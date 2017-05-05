
def check_core(types,args,sep,level):
    if not types:
        return []
    elif isinstance(types,dict):
        return Process_dict(types,args,sep,level)
    elif isinstance(types,tuple):
        return Process_tuple(types,args,sep,level)
    elif isinstance(types,list):
        return Process_list(types,args,sep,level)
    else:
        return Process(types,args,sep,level)
            

def Process_dict(types,args,sep,level):
    for i in types.keys():
        k=args.find(sep) if sep and args.find(sep)!= -1 else None
        tempres=check_core(i,args[:k],sep,level+1)
        if tempres:
            tempres2=check_core(types[i],args[k+1 if k else None:],sep,level+1)
            if tempres2!=None:
                return tempres+tempres2
            else:
                return None

def Process_list(types,args,sep,level):
    result=[]
    for i in types:
        k=args.find(sep) if sep and args.find(sep)!=-1 else None
        r=check_core(i,args[:k],sep,level+1)
        if r!=None:
            result+=r
            if k:
                args=args[k+1:]
            else:
                args=''
        else:
            return None
    if not level and args!='':
        return None
    return result


def Process_tuple(types,args,sep,level):
    res=None
    for i in types:
        try:
            if res!=None:
                if callable(i):
                    temp=i(res)
                else:
                    return check_core(i,temp,sep,level+1)
            else:
                k=args.find(sep) if sep and args.find(sep)!=-1 else None
                if callable(i):
                    temp=i(args[:k])
                else:
                    return check_core(i,args[:k],sep,level+1)
            if not isinstance(temp,bool):
                res=temp
            elif not temp:
                return None
            elif res==None:
                res=args[:k]
        except Exception as e:
            print(e)
            return None
    return [res]


def Process(types,args,sep,level):
    try:
        result=types(args)
        return [result] if not isinstance(result,bool) else [args] if result else None
    except:
        if types==args:
            return [args]
        elif types==args.upper():
            return [args.upper()]
        return None

def check_type(types,errormessage='ERROR',hint='',sep=' '):
    while True:
        args=input(hint)
        result=check_core(types,args,sep,0)
        if result!=None:
            if len(result)!=1:
                return result
            else:
                return result[0]
        print(errormessage)
    






