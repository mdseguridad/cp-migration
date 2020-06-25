#!/usr/bin/env python3

# -*- coding: utf-8 -*


import time,argparse,random
import xml.etree.ElementTree as ET

colors = [ 'aquamarine', 'black', 'blue', 'crete blue', 'burlywood', 'cyan', 'dark green', 'khaki', 'orchid', 'dark orange', \
'dark sea green', 'pink', 'turquoise', 'dark blue', 'firebrick', 'brown', 'forest green', 'gold', 'dark gold', \
'gray', 'dark gray', 'light green', 'lemon chiffon', 'coral', 'sea green', 'sky blue', 'magenta', 'purple', 'slate blue',\
 'violet red', 'navy blue', 'olive', 'orange', 'red', 'sienna', 'yellow']

parser = argparse.ArgumentParser(description='exportamos un objeto de las politicas de Checkpoint')
parser.add_argument('objectfile',help='fichero xml con los objetos')
parser.add_argument('object2find',help='objeto a exportar')
parser.add_argument('-t','--tag', help='tag', default='python')


args = parser.parse_args()
ficheroObjects = args.objectfile
objectFind = args.object2find
tag = args.tag
commandTail ='ignore-warnings true -s id.txt'


def parseNetworksObjects(netObjects):
    objectList = []
    tmpObjects = netObjects.find('members')
    tmpObjects = tmpObjects.findall('reference')
    for i in tmpObjects:
        j = i.find('Name')
        objectList.append(j.text)
    return objectList


def prettyGroup(objects):
    tmpList = list(objects)
    if (len(tmpList) > 1):
        groupString = "'["
        for i in tmpList[0:-1]:
            groupString = groupString + '"'+ i + '", '
        groupString = groupString + '"'+ tmpList[-1] + '"'
        groupString = groupString + "]'"
    elif (len(tmpList) == 1):
        groupString = '"' + tmpList[0] + '"'
    else:
        groupString = '"ErrorRaro"'
    return groupString

def expandGroup (recordList, allRecordGroups):
    backList = []
    for i in recordList:
         if (i in allRecordGroups):
             backList.extend(expandGroup(allRecordGroups[i].split(','),allRecordGroups))
             backList.append(i)
         else:
             backList.append(i)
    #backList = set(backList)
    return backList
    
def getObjetcs(objectsXML):
    allNetObject = dict()
    allNetGroup = dict()
    for child in objectsXML:
       type = child.find('type').text
       color = child.find('color').text
       if ((color == 'black') or (color not in colors)):
           color = random.choice(colors)
       comments = child.find('comments').text
       if (comments != None):
           comments =  comments + ' importado: ' + fecha
       else:
           comments = 'Importado el : ' + fecha   
       # Datos para redes
       if (type == 'network'):
           line = 'mgmt_cli add-network name "' + child.find('Name').text +'" subnet ' + \
           child.find('ipaddr').text + ' subnet-mask '+ child.find('netmask').text + ' tags "' + tag +\
           '" color "' + color + '" comments "' + comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para hosts
       elif (type == 'host'):
           line = 'mgmt_cli add-host name "' + child.find('Name').text + '" ip-address ' + \
           child.find('ipaddr').text + ' tags "' + tag + '" color "' + color + '" comments "' + \
           comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para rangos
       elif (type == 'machines_range'):
           line = 'mgmt_cli add address-range name "' + child.find('Name').text + '" ip-address-first ' + \
           child.find('ipaddr_first').text + ' ip-address-last '+ child.find('ipaddr_last').text + \
           ' tags "' + tag +'" color "' + color + '" comments "' + comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para grupos
       elif ((type == 'cluster_member') or (type == 'gateway') or (type == 'gateway_cluster')):
           line = 'mgmt_cli add-host name "' + child.find('Name').text + '" ip-address 127.0.0.1 ' + \
           ' tags "Dummy" color "pink" comments "Dummy:' + type + ' -- ' + \
           comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       elif (type == 'group'):
           groupMembers = parseNetworksObjects(child)
           if groupMembers:
               line = 'mgmt_cli add group name "' + child.find('Name').text + '" members ' + prettyGroup(groupMembers) +\
               ' tags "' + tag +'" color "' + color + '" comments "'+ '" ' + commandTail
           else:
               line = 'mgmt_cli add group name "' + child.find('Name').text  +\
               '" tags "' + tag +'" color "' + color + '" comments "'+ '" ' + commandTail
           allNetObject[child.find('Name').text] = line
           allNetGroup[child.find('Name').text] = ','.join(groupMembers)
    return allNetObject, allNetGroup
  

fecha = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 
print ('# fichero de objetos:' , ficheroObjects)
print ('# fecha: ', fecha)
print ()


try:
    treeObjects = ET.parse(ficheroObjects)
except:
    print ('Error leyendo el fichero: ', ficheroObjects)
    exit()

rootObjects = treeObjects.getroot()
# Proceso de objetos
allNetObject,allNetGroup = getObjetcs(rootObjects)

# proceso los grupos objetos de  que aparezan
#netList.remove('Any')

print ('# Info')
print ('# Total network objects:',len(allNetObject))
print ('# Total network groups:',len(allNetGroup))
print ('')
print ('## Network Object to export',objectFind)

if objectFind in allNetObject:
    if objectFind in allNetGroup:
        netList = []
        netList.extend(expandGroup([objectFind], allNetGroup))
        for j in netList:
            print (allNetObject[j])
    else:
        print (allNetObject[objectFind])
else:
    print ('Object ',objectFind,'not in network object db')
