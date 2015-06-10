import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx
import os
import pymel.core
import copy
import maya.OpenMayaAnim as omAm
import random
import math


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

def ConnectNode( targetNode, sourceNode, attrName):
	fnDpendTargetNode = OpenMaya.MFnDependencyNode(targetNode)
	fnDependSourceNode = OpenMaya.MFnDependencyNode(sourceNode)
	
	source_str =  fnDependSourceNode.name() +"_" + attrName +".output"
	dest_str = fnDpendTargetNode.name() + "." + attrName

	print "dest_str= " + dest_str
	print "source_str= " + source_str
	cmds.connectAttr(source_str, dest_str)
	
####################################################
##                  main                          ##
####################################################


#object selection
selection = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(selection)
iter = OpenMaya.MItSelectionList(selection)

sourceNode = OpenMaya.MObject()
selection.getDependNode( 0, sourceNode )

targetNode = OpenMaya.MObject()
selection.getDependNode( 1, targetNode)

#ConnectNode(targetNode, sourceNode, "translateX")
#ConnectNode(targetNode, sourceNode, "translateY")
#ConnectNode(targetNode, sourceNode, "translateZ")
ConnectNode(targetNode, sourceNode, "rotateX")
ConnectNode(targetNode, sourceNode, "rotateY")
ConnectNode(targetNode, sourceNode, "rotateZ")

