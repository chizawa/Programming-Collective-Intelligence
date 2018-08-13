# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 21:00:48 2018

@author: Administrator
"""
import numpy as np
import random
from PIL import Image,ImageDraw

def readfile(filename):
    with open('blogdata.txt') as f:
        lines = f.readlines()
        colnames = lines[0].strip().split('\t')[1:]
        rownames = []
        data = []
        for line in lines[1:]:
            p = line.strip().split('\t')
            rownames.append(p[0])
            data.append([float(x) for x in p[1:]])
        return rownames,colnames,data
            
    
def pearson(v1,v2):
    similarity = np.corrcoef(v1,v2)[1,0]
    return 1.0-similarity

def tanimoto(v1,v2):
    '''数据集只有1和0两种取值代表有无，Taminoto系数用于度量两个向量的重叠程度'''
    c1,c2,shr=0,0,0
    for i in range(len(v1)):
        if v1[i]!=0:    c1+=1
        if v2[i]!=0:    c2+=1
        if v1[i]!=0 and v2[i]!=0:   shr+=1
    return 1.0-shr/(c1+c2-shr)


class bicluster(object):
    def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
        self.left = left    #聚类的左右节点
        self.right = right
        self.distance = distance
        self.vec = vec
        self.id = id
        
def hcluster(rows,distance=pearson):
    distances = {}
    currentclsutid = -1

    #最开始的聚类是数据集中的行
    clust = [bicluster(rows[i],id=i) for i in range(len(rows))]

    while len(clust)>1:
        lowestpair = (0,1)
        closest = distance(clust[0].vec,clust[1].vec)

        #遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                #用distances缓存距离的计算值
                if (clust[i].id,clust[j].id) not in distances:
                    distances[(clust[i].id,clust[j].id)] = distance(clust[i].vec,clust[j].vec)
                d = distances[(clust[i].id,clust[j].id)]

                if d<closest:
                    closest = d
                    lowestpair = (i,j)

        #计算两个聚类的平均值
        mergevec = [(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))]

        #建立新的聚类
        newcluster = bicluster(mergevec,id=currentclsutid,distance=closest,
                               left=clust[lowestpair[0]],right=clust[lowestpair[1]])

        #不在原始集合中的聚类，id为负数
        currentclsutid -= 1
        #在cluster中去除已聚类的，添加聚类
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]


def printcluster(clust,labels=None,n=0):
    #利用缩进来建立层级布局
    for i in range(n):
        print(' ',end=' ')

    if clust.id<0:
        #负数标记代表这是一个分支
        print('-')
    else:
        #正数标记代表这是一个叶节点
        if labels==None:    
            print(clust.id)
        else:
            print(labels[clust.id])

    #开始打印左右侧分支
    if clust.left!=None:
        printcluster(clust.left,labels=labels,n=n+1)
    if clust.right!=None:
        printcluster(clust.right,labels=labels,n=n+1)
        
 
 #返回聚类的总体高度
def getheight(clust):
    #叶节点返回1
    if clust.left==None and clust.right==None:
        return 1
    #否则高度为每个分支的高度之和
    else:
        return getheight(clust.left)+getheight(clust.right)

#返回树的距离
def getdepth(clust):
    if clust.left==None and clust.right==None:  return 0
    #一个枝节点的距离等于左右分支中距离较大者加上该枝节点自身的距离
    else:   return max(getdepth(clust.left),getdepth(clust.right))+clust.distance


#生成图片
def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
    #高度和宽度
    h=getheight(clust)*20
    w=1200
    depth=getdepth(clust)
    #对距离值做相应调整
    scaling = float(w-150)/depth
    #新建白色背景的图片
    img=Image.new('RGB',(w,h),(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))
    #画第一个节点
    drawnode(draw,clust,10,h/2,scaling,labels)

    img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling,labels):
    if clust.id<0:
        h1 = getheight(clust.left)*20
        h2 = getheight(clust.right)*20
        top = y-h2/2
        bottom = y+h1/2
        #线的长度
        ll = clust.distance*scaling
        #聚类到其子类节点的垂直线
        draw.line((x,top,x,bottom),fill=(255,0,0))
        #连接左右侧节点的水平线
        draw.line((x,top,x+ll,top),fill=(255,0,0))
        draw.line((x,bottom,x+ll,bottom),fill=(255,0,0))
        #递归绘制左右节点
        drawnode(draw,clust.left,x+ll,top,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom,scaling,labels)

    else:
        #如果是一个叶节点，绘制叶节点的标签
        draw.text((x+5,y-7),labels[clust.id],(0,0,0))

#列聚类        
def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata


#K-means clustering
def kcluster(rows,distance=pearson,k=4):
    #确定每个点的最大值和最小值
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))]
    #随机创建k个中心点
    clusters = [[random.random()*(ranges[i][1]-ranges[i][0]) for i in range(len(rows[0]))]for j in range(k)]
    lastmatches = None
    #开始
    for t in range(100):
        print('Iteration %d'%t)
        bestmatches = [[] for i in range(k)]
        #在每一行中寻找最近的中心点
        for i in range(len(rows)):
            row = rows[i]
            bestmatch = 0
            for j in range(k):
                d = distance(row,clusters[j])
                if d<distance(row,clusters[bestmatch]):
                    bestmatch = j
            bestmatches[bestmatch].append(i)

        #如果结果与上次的相同，聚类结束
        if bestmatches==lastmatches:    break
        lastmatches=bestmatches
        #把中心点移到其所有成员的平均位置处
        for i in range(k):
            if len(bestmatches[i])>0:
                filter_cluster = [rows[j] for j in bestmatches[i]]
                clusters[i]=[np.mean([row[j] for row in filter_cluster]) for j in range(len(rows[0]))]
    return bestmatches


#二维缩放（在二维平面上展示数据）
def scaledown(data,distance=pearson,rate=0.01):
    '''接受一个数据向量作为参数，返回一个包含两列的向量，即二维图上的xy坐标'''
    n=len(data)
    #每一对数据项之间的真实距离
    realdist = [[distance(data[i],data[j]) for i in range(n)] for j in range(n)]
    outersum = 0.0

    #随机初始化节点在二维空间的起始位置
    loc = [[random.random(),random.random()] for i in range(n)]
    fakedist = [[0.0 for i in range(n)] for j in range(n)]

    lasterror = None
    for m in range(0,1000):
        #寻找投影后的距离
        for i in range(n):
            for j in range(n):
                fakedist[i][j]=np.sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))
        #移动节点
        grad = [[0.0,0.0] for i in range(n)]
        totalerror = 0
        for k in range(n):
            for j in range(n):
                if j==k:    continue
                errorterm = (fakedist[j][k]-realdist[j][k])/realdist[j][k]
                #每个节点都需要根据误差的多少，按比例移离或移向其他节点
                grad[k][0] = (loc[k][0]-loc[j][0])/fakedist[j][k]*errorterm
                grad[k][1] = (loc[k][1]-loc[j][1])/fakedist[j][k]*errorterm
                totalerror+=abs(errorterm)


        print(totalerror)

        #如果节点移动之后的结果更糟，结束程序
        if lasterror and lasterror<totalerror:break
        lasterror=totalerror
        #根据rate和grad的值相乘的结果，移动每一个节点
        for k in range(k):
            loc[k][0]-=rate*grad[k][0]
            loc[k][1]-=rate*grad[k][1]

    return loc

def draw2d(data,labels,jpeg='mds2d.jpg'):
    img=Image.new('RGB',(2000,2000),(255,255,255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x=(data[i][0]+0.5)*1000
        y=(data[i][1]+0.5)*1000
        draw.text((x,y),labels[i],(0,0,0))
    img.save(jpeg,'JPEG')


filename = 'blogdata.txt'
blogname,words,data = readfile(filename)
clust = hcluster(data)
drawdendrogram(clust,blogname,jpeg='blogclust.jpg')

kclust = kcluster(data)
coords=scaledown(data)
draw2d(coords,blogname,jpeg='blogs2d.jpeg')

#
#rdata = rotatematrix(data)
#wordclust = hcluster(rdata)
#drawdendrogram(wordclust,words,jpeg='wordclust.jpg')