import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx
import os
import pymel.core
import copy
import maya.OpenMayaAnim as omAm
import random
import math


##########################################
# todo: change this function name to more clear name.
def OutputAnimCurve(obj):
	fn = omAm.MFnAnimCurve(obj)

	dependNodeFunc = OpenMaya.MFnDependencyNode(obj)
	prefixStr =  "static float " + dependNodeFunc.name() + "[] = "

	#keycount
	iKeyCount = fn.numKeys()
	if iKeyCount == 0: return

	#print "KeyCounts: " + str(iKeyCount)
	keyframesStr = "{ "
	for i in range(iKeyCount):
		keyTime = fn.time(i).value()
		keyValue = fn.value(i)
		#print ("time: " +  str(keyTime))
		keyframesStr += (str(keyValue) + ", ")
		#print
	keyframesStr = keyframesStr.rstrip(", ")
	keyframesStr = keyframesStr + " };"
	return prefixStr + keyframesStr
	#print keyframesStr



##########################################################
#Get a connected node wiht selected (Node, AttributeName)
# return plugedNode
def GetConnectedNode(dependNode, attrName):
	fnDependNode = OpenMaya.MFnDependencyNode(dependNode)
	attr = fnDependNode.attribute(attrName)
	plug = OpenMaya.MPlug(dependNode, attr)
	inPlugArray = OpenMaya.MPlugArray()
	plug.connectedTo(inPlugArray, True, False)
	plugedNode = inPlugArray[0].node()
	return plugedNode


##########################################################
def PrintTranslateAnimation(node):
	testNodeX = GetConnectedNode(node, "translateX")
	str = OutputAnimCurve(testNodeX) + "\n"

	testNodeY = GetConnectedNode(node, "translateY")
	str = str + OutputAnimCurve(testNodeY) + "\n"

	testNodeZ = GetConnectedNode(node, "translateZ")
	str = str + OutputAnimCurve(testNodeZ) + "\n\n"

	#print str

def PrintRotateAnimation(node):
	testNodeX = GetConnectedNode(node, "rotateX")
	#str = OutputAnimCurve(testNodeX) + "\n"
	fnX = omAm.MFnAnimCurve(testNodeX)

	testNodeY = GetConnectedNode(node, "rotateY")
	#str = str + OutputAnimCurve(testNodeY) + "\n\n"
	fnY = omAm.MFnAnimCurve(testNodeY)

	#keycount
	iKeyCount = fnX.numKeys()
	if iKeyCount == 0: return

	#print "KeyCounts: " + str(iKeyCount)
	keyframesStr = "{ "

	strX = "{ "
	strY = "{ "
	strZ = "{ "
	for i in range(iKeyCount):

		#get rotX
		keyTimeX = fnX.time(i).value()
		keyValueX = fnX.value(i)
		radX  = keyValueX / 180.0 * math.pi


		#get rotY
		keyTimeY = fnY.time(i).value()
		keyValueY = fnY.value(i)
		radY =  keyValueY / 180.0 * math.pi
		#make x,y,z
		vx =  math.cos(radX - 0.5*math.pi) * math.cos(radY)
		vy =  math.sin(radX - 0.5*math.pi)
		vz = -math.cos(radX - 0.5*math.pi) * math.sin(radY)

		strX += (str(vx) + ", ")
		strY += (str(vy) + ", ")
		strZ += (str(vz) + ", ")

	strX = strX.rstrip(", ")
	strY = strY.rstrip(", ")
	strZ = strZ.rstrip(", ")

	strX = strX + " };\n"
	strY = strY + " };\n"
	strZ = strZ + " };\n"
	#return prefixStr + keyframesStr
	#testNodeZ = GetConnectedNode(node, "rotateZ")
	#str = str + OutputAnimCurve(testNodeZ) + "\n\n"

	print strX
	print strY
	print strZ

####################################################
finalOutputString = '''LightingMnagaer::Config pointlight_animation_configuration = \n \
{\n \
	{ 0.0 , 0.0, 0.0 }, // ambient \n \
	{ 0.0 , -1.0, 0.0 }, // sun light direction \n \
	{ 0.0 , 0.0, 0.0 }, // sun light color \n     \
'''

# print finalOutputString



####################################################




####################################################
##                  main                          ##
####################################################


#object selection
selection = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(selection)
iter = OpenMaya.MItSelectionList(selection)
dependNode = OpenMaya.MObject()
selection.getDependNode( 0, dependNode )
#select object iteration

finalOutputString = finalOutputString + str(selection.length()) + 	", // num of point lights \n"
finalOutputString += "	0, // num of spot lights \n\n"
finalOutputString += "	{ \n"
while not iter.isDone():
	iter.getDependNode(dependNode)
	#	PrintTranslateAnimation(dependNode)
	PrintRotateAnimation(dependNode)
	'''
	# ヘッダ部分作成
	finalOutputString += '		{\n \
			{0.0f, 0.0f, 0.0f}, // position \n'

	colorR = random.random()
	colorG = random.random()
	colorB = random.random()
	if (colorR + colorG < 1) :
		temp = 1 - colorR  - colorG;
		colorB = random.uniform(temp , 1)

	finalOutputString += "			{ " + str(colorR) + ", " + str(colorG) + ", " +  str(colorB) + "}, // color \n"
	#get pointlightData
	finalOutputString += "			10000, // intensity \n"
	finalOutputString += "			500,   // radius \n"
	finalOutputString += "			180,   // animation size \n"

	finalOutputString +=  "			// animation(position) \n"

	tXNode   = GetConnectedNode(dependNode, "translateX")
	tXNodeFunc = OpenMaya.MFnDependencyNode(tXNode)

	tYNode   = GetConnectedNode(dependNode, "translateY")
	tYNodeFunc = OpenMaya.MFnDependencyNode(tYNode)

	tZNode   = GetConnectedNode(dependNode, "translateZ")
	tZNodeFunc = OpenMaya.MFnDependencyNode(tZNode)

	finalOutputString +=  "			{ " + tXNodeFunc.name() + ", " + tYNodeFunc.name() + ", " + tZNodeFunc.name() +"}, \n"
	finalOutputString +=  "			// animation(color) \n"
	finalOutputString +=  "			{ nullptr, nullptr, nullptr }, \n"
	finalOutputString +=  "			// animation(intensity) \n"
	finalOutputString +=  "			nullptr \n		}, 	\n"

	'''
	iter.next()

finalOutputString += "	}, \n"
finalOutputString += "	\n	{} // no spot lights \n}"
#print finalOutputString
