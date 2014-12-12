import os
from com.thoughtworks.xstream import XStream
from com.thoughtworks.xstream.io.xml import DomDriver
    
def makeopen(filename):
    
    thedir=os.path.split(filename)[0]
    
    if not os.path.isdir(thedir):
        os.makedirs(thedir)
    
    assert os.path.isdir(thedir), "cannot make the directory %s" % thedir
    
    file=open(filename,'w')
    
    return file

def readObjectFromFile(filename):    
    file = open(filename,'r')
    
    xstream=XStream(DomDriver()) 
    object=xstream.fromXML(file.read())
    
    file.close()
    
    return object

def writeObjectToFile(object,filename):     
    file=makeopen(filename)
    
    xstream=XStream(DomDriver()) 
    file.write(xstream.toXML(object))
    
    file.close()