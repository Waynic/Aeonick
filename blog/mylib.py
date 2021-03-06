# -*- coding: utf-8 -*-
from blogDB import get_db

#定义类
class password:
    def __init__(self,pwd):
        self.pwd = pwd
    def check(self):
        import hashlib
        m = hashlib.md5()
        if self.pwd:
            self.pwd +=  '1396'
        else:
            return False
        m.update(self.pwd)
        if m.hexdigest()=='01bf2bf3375b3fbaf8d2dac6dad08c84':
            return True
        else:
            return False

class Article:
    def __init__(self, id):
        self.id = id
    def getExit(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('SELECT id, title, abstract, tag, date, file FROM blog where id = ?',(self.id,))
        self.exit = cur.fetchall()[0]
        return self.exit
    def getArti(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('SELECT title, date, content, tag, abstract from blog where id = ?',(self.id,))
        self.arti = cur.fetchall()[0]
        return self.arti
    def getEdit(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('SELECT title, content,tag from blog where id = ?',(self.id,))
        content = cur.fetchall()[0]
        self.title = content[0]
        self.content = content[1]
        self.tag = content[2]
    def update(self, title, tag, img, file, content):
        abstract = abstr(content,img)
        tags = (tag or '').replace('，',',')
        blogdb = get_db()
        cur = blogdb.cursor()
        if self.id:
            cur.execute('UPDATE blog SET title = ? ,content = ?,abstract = ?,tag = ? ,file = ? WHERE ID = ?;', (title, content,abstract,tags,file, self.id))
        else:
            cur.execute('insert into blog (title,tag,file,abstract,content) values (?, ?, ?, ?, ?)', (title,tag,file,abstract,content))
            cur.execute('select id from blog order by id desc limit 1')
            blog = cur.fetchall()
            self.id = blog[0][0]
        blogdb.commit()
        cur.execute('delete from tag where blog = ?',(self.id,))
        tags = tags.split(',')
        for tag in tags:
            cur.execute('insert into tag (tag, blog) values (?, ?)', (tag, self.id))
        blogdb.commit()
    def delArti(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('DELETE FROM blog WHERE id = ? ',(self.id,))
        cur.execute('DELETE FROM tag WHERE blog = ? ',(self.id,))
        cur.execute('DELETE FROM comm WHERE blog = ? ',(self.id,))
        blogdb.commit()

class comment:
    def __init__(self, id = 0 ):
        self.id = id
    def commList(self):
        try:
            blogdb = get_db()
            cur = blogdb.cursor()
            cur.execute(' SELECT content, date, author, id, reply FROM comm WHERE blog = ? ORDER BY id DESC',(self.id,))
            temp = cur.fetchall() or []
            temp = list(temp)
            temp = map(lambda x:list(x),temp)
            def coSort(x,y):
                xId = x[4] or x[3]
                yId = y[4] or y[3]
                if xId<yId:
                    return 1
                else:
                    return -1
            temp = sorted(temp, coSort)
            def coVeri(x):
                x[4] = x[4] or x[3]
                diff = x[4]-x[3]
                x[4] = diff and u're'
                return x
            self.cList = map(coVeri,temp)
        except:
            self.cList = []
        finally:
            return self.cList
    def getNew(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute(' SELECT content, date, author, id, blog FROM comm ORDER BY id DESC LIMIT 12')
        temp = cur.fetchall() or []
        self.cList = temp
        return self.cList
    def insert(self, content, author, reply):
        author = author or u'访客'
        reply = reply or None
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('insert into comm (content, author, blog, reply) values (?, ?, ?, ?)', (content, author, self.id, reply))
        blogdb.commit()
    def dele(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        cur.execute('DELETE FROM comm WHERE id = ? ',(self.id,))
        blogdb.commit()

class artiList:
    def __init__(self,method = '',key = '',page = 1):
        self.method = method
        self.key = key
        self.page = ( page - 1 ) * 8
    def getAl(self):
        result = []
        for arti in self.al:
            temp = Article(arti)
            temp = temp.getExit()
            result.append(temp)
        self.result = result
        return self.result
    def getLen(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        if self.method == 'file':
            cur.execute('SELECT count(*) FROM blog WHERE file = ?;',(self.key,))
        elif self.method == 'tag':
            cur.execute('SELECT count(*) FROM tag WHERE tag = ?;',(self.key,))
        else:
            cur.execute('SELECT count(*) FROM blog;')
        rawlen = cur.fetchall()
        rawlen = int(rawlen[0][0])
        self.len = (rawlen+7)/8 or 1
        return self.len
    def alUpdate(self):
        blogdb = get_db()
        cur = blogdb.cursor()
        if self.method == 'file':
            cur.execute(' SELECT id FROM blog WHERE file = ? ORDER BY id DESC LIMIT 8 OFFSET ?',(self.key,self.page,))
        elif self.method == 'tag':
            cur.execute('select blog from tag where tag = ? LIMIT 8 OFFSET ?',(self.key,self.page,))
        else:
            cur.execute(' SELECT id FROM blog ORDER BY id DESC LIMIT 8 OFFSET ?',(self.page,))
        altemp = cur.fetchall()
        altemp = map(lambda x: int(x[0]),altemp)
        altemp.sort(reverse = True)
        self.al = altemp
        return self.al



#摘要生成函数，这个实现方式比较蠢，还有一个更快的在aids.py里，但很难看
def abstr(text,img = ""):
    text = text[:1200]
    text = text.replace(u'&nbsp;',u' ')
    text = text.replace(u'</p',u'\n<')
    text = text.replace(u'</b',u'\n<')
    text = text.replace(u'</h',u'\n<')
    text = text.replace(u'<br>',u'\n')
    def fn(x, y):
        if x[-1] == "<" and y != ">":
            return x
        else:
            return x+y
    text = reduce(fn,text)
    text = text.replace(u'<>',u'')
    text = text.replace(u'\n\n\n',u'\n')
    text = text.replace(u'\n\n',u'\n')
    print text
    text = text[:120]+'...'+'<center>'+'<img src="'+img+'">'+'</center>'
    return text
