import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx
import os
import pymel.core
import copy



def GetBaseTextureFullPathFileName(currrentInMeshFnMesh):
	numInstance = currrentInMeshFnMesh.parentCount()

	objectArray    = OpenMaya.MObjectArray()
	testIntArray   = OpenMaya.MIntArray()
	currrentInMeshFnMesh.getConnectedShaders(0, objectArray, testIntArray);
	#print "instance0::material num=" + str(objectArray.length())
	#print objectArray[0].apiTypeStr()

	#get dependency from the object's ShadingEngine
	dependencyNode = OpenMaya.MFnDependencyNode(objectArray[0])
	print "DG Node Name= " + str(dependencyNode.name())
	#print "Plugin Name= "  + str(dependencyNode.pluginName())

	plugArray = OpenMaya.MPlugArray()
	dependencyNode.getConnections(plugArray)

	#print "Plug Array length= " +  str(plugArray.length())

	plug = dependencyNode.findPlug("surfaceShader")
	#plug = dependencyNode.findPlug("phong")
	#print plug.name()

	materials = OpenMaya.MPlugArray()
	plug.connectedTo(materials, True, False)

	materialName =""
	# mateiral
	if materials.length() != 0:
		material = OpenMaya.MFnDependencyNode(materials[0].node())
		print material.name()
		material_plugs = OpenMaya.MPlugArray()
		material.getConnections(material_plugs)
		#for i in range(0, material_plugs.length()):
		#	print material_plugs[i].name()
		#baseTexture = material.findPlug("outColor")
		baseTexture = material.findPlug("color")
		materialName = baseTexture.name()
		#print materialName
		
		materialAttr = materialName.partition("_")[0]
		#print materialAttr
		useAlphaTest = False
		if materialAttr == "MA" :
			useAlphaTest = True
		
	
		#texture sampler
		texturePlugs = OpenMaya.MPlugArray()
		baseTexture.connectedTo(texturePlugs, True, False)

		if texturePlugs.length != 0:
			#for i in range(0, texturePlugs.length()):
			#	print texturePlugs[i].name()

			textureNode = OpenMaya.MFnDependencyNode(texturePlugs[0].node())
			print textureNode.name()
			fileNamePlug = textureNode.findPlug("fileTextureName")
			fileName = pymel.core.datatypes.getPlugValue(fileNamePlug)
			#fileNamePlug.getValue(fileName)
			print fileName
			return fileName, useAlphaTest
	else:
		print "???"

	return ""




def MakeShapeNodeStringImp(dagPath, hasInstance, instanceNum, instanceMat):
	nodeName = dagPath.partialPathName()

	# create empty point array
	inMeshMPointArray = OpenMaya.MPointArray()
	inMeshNormalArray = OpenMaya.MFloatVectorArray()
	inMeshUArray	  = OpenMaya.MFloatArray()
	inMeshVArray	  = OpenMaya.MFloatArray()
	inMeshVerticesIDPerFaceArray  = OpenMaya.MIntArray()
	inMeshVerticesNumPerFaceArray = OpenMaya.MIntArray()

	# create function set and get points in world space
	currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
	currentInMeshMFnMesh.getPoints( inMeshMPointArray,  OpenMaya.MSpace.kWorld)
	currentInMeshMFnMesh.getNormals(inMeshNormalArray, OpenMaya.MSpace.kWorld)
	currentInMeshMFnMesh.getUVs(         inMeshUArray, inMeshVArray)
	currentInMeshMFnMesh.getVertices(inMeshVerticesNumPerFaceArray, inMeshVerticesIDPerFaceArray)

	# put each point to a list
	pointList = []
	normalList = []
	uvList	= []
	faceList  = []

	iterator_vertices = maya.OpenMaya.MItMeshVertex(dagPath)
	num_vertices = iterator_vertices.count()

	#iteration each verticies
	while not iterator_vertices.isDone():
		world_point = iterator_vertices.position(OpenMaya.MSpace.kWorld)
		pointList.append([world_point.x, world_point.y, world_point.z])

		normal = OpenMaya.MVector()
		iterator_vertices.getNormal(normal)
		normalList.append( [normal.x, normal.y, normal.z])

		uv = OpenMaya.MScriptUtil()
		p_array = [0, 0]
		uv.createFromList(p_array, 2)
		uv_point = uv.asFloat2Ptr()
		iterator_vertices.getUV(uv_point)
		one_uv = [OpenMaya.MScriptUtil.getFloat2ArrayItem( uv_point, 0, 0 ), OpenMaya.MScriptUtil.getFloat2ArrayItem( uv_point, 0, 1 )]

		# for PS4 texcoordinate
		one_uv[1] = 1.0 - one_uv[1]
		uvList.append(one_uv)

		str_normal = "normal=" + str(normal.x) + "," + str(normal.y) + "," + str(normal.z)
		str_uv     = "uv    =" + str(one_uv)

		iterator_vertices.next()

	# Create Face...
	i_counter = 0
	for i in range( inMeshVerticesNumPerFaceArray.length()):
		perFaceList =[]
		for j in range( inMeshVerticesNumPerFaceArray[i]):
			perFaceList.append(inMeshVerticesIDPerFaceArray[i_counter])
			i_counter += 1
		faceList.append(perFaceList)


	#Create Cpp Code as String...
	namespace_begin_str  = "namespace " + nodeName.rpartition("|")[2] + "{\n"
	namespace_end_str    = "}  "
	num_vertices_str     = 'unsigned int num_vertices = '     + str(num_vertices) + ";\n"
	num_face_indices_str = 'unsigned int num_face_indices = ' + str(i_counter)  + ";\n"

	position_str = 'float positions[] = { \n'
	for i in pointList:
		for j in i:
			position_str += str(j)
			position_str += ","
		position_str += "\n"
	position_str = (position_str.rpartition(","))[0]
	position_str += '};\n\n\n'

	normal_str   = ' float normals[] = { \n'
	for i in normalList:
		for j in i:
			normal_str += str(j)
			normal_str += ","
		normal_str += "\n"
	normal_str = (normal_str.rpartition(","))[0]
	normal_str += '};\n\n\n'

	uv_str	     = ' float texcoords[] = { \n'
	for i in uvList:
		for j in i:
			uv_str += str(j)
			uv_str += ","
		uv_str += "\n"
	uv_str = (uv_str.rpartition(","))[0]
	uv_str += '};\n\n\n'

	index_str	 = 'uint16_t indices[] = { \n'
	for i in faceList:
		for j in i:
			index_str += str(j)
			index_str += ","
		index_str += "\n"
	index_str = (index_str.rpartition(","))[0]
	index_str += '};\n\n\n'

	
	#Texure Section
	useAlpha = False
	texture_filename_fullpath, useAlpha = GetBaseTextureFullPathFileName(currentInMeshMFnMesh)
	texture_filename_fullpath_no_ext = (texture_filename_fullpath.rsplit('.'))[0]
	texture_filename_no_ext          = (texture_filename_fullpath_no_ext.rsplit('/', 1))[1]

	gnm_texture_filename_fullpath    = texture_filename_fullpath_no_ext + ".gnf"
	gnm_texture_filename             = texture_filename_no_ext          + ".gnf"
	#print gnm_texture_filename_fullpath
	
	
	#create Gnm Texture
	batch_full_path = "F:\\workspace\\2014PS4Seminar\\ZCulling\\grass_test\\scripts\\CreateGnmTexture.bat"
	batch_call_code = batch_full_path + " " + texture_filename_fullpath + " " + gnm_texture_filename_fullpath
	os.system(batch_call_code)

	#instance check...
	instance_str=""
	if hasInstance:
		instance_str  = "bool has_instance = true;\n"
	else :
		instance_str  = "bool has_instance = false;\n"
	
	instance_str += "unsigned int num_instance = " + str(instanceNum) + ";\n"
	instance_str += instanceMat

	output_str  = ""
	output_str += namespace_begin_str  
	output_str += num_vertices_str
	output_str += num_face_indices_str + "\n"
	output_str += position_str 
	output_str += normal_str   
	output_str += uv_str       
	output_str += index_str
	output_str += instance_str
	
	output_str += ("char* texture_name=\""           + gnm_texture_filename          + "\";\n")
	output_str += ("char* texture_fullpath_name=\"" + gnm_texture_filename_fullpath + "\";\n")
	if useAlpha :
		output_str += "bool use_alpha_test = true;\n"
	else :
		output_str += "bool use_alpha_test = false;\n"
	
	output_str +=(namespace_end_str) + "// namespace "  + nodeName + "\n\n\n"
	return output_str, nodeName.rpartition("|")[2]

def MakeShapeNodeString(dagPath):
	return MakeShapeNodeStringImp(dagPath, False, 0, "")



#object selection
selection = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(selection)
#ここでメッシュじゃなくてDAGをひっぱってくる
iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
dagPath = OpenMaya.MDagPath()
iterDag = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kMesh)
dagPathArray = OpenMaya.MDagPathArray()

shapeNodeList = []
shapeDic      = {}
shapeDagPathList   =[]

# 最終的なファイル出力用String.
cppTransformStr  = "namespace ZCullTestScene{\n"
worldMatDic = {}
# transform node check...
while not iterDag.isDone():
	iterDag.getPath(dagPath)
	#print dagPath.fullPathName()
	fullDagPathName = dagPath.fullPathName()
	fullDagPathName = str(fullDagPathName)
	
	transformName = ""
	nativeTransformName = fullDagPathName.rpartition("|")[0]
	transformName = fullDagPathName.rpartition("|")[0]
	transformName =  "T"  + transformName.replace("|", "_")
	#print  "transform name = " + transformName
	

	modelMatrix = dagPath.inclusiveMatrix()

	stringMatrix = ""
	stringMatrix = "float " + transformName + "[16]={"
	tempStringMatrix =""
	for i in range(4):
		for j in range(4):
			stringMatrix +=str( modelMatrix(i, j))
			stringMatrix +=", "
			
			tempStringMatrix +=str( modelMatrix(i, j))
			tempStringMatrix +=", "
	stringMatrix = (stringMatrix.rpartition(","))[0]
	stringMatrix += "};"
	#print stringMatrix
	cppTransformStr += stringMatrix + "\n"
	
	#shape node check...
	shapeName     = fullDagPathName.rpartition("|")[2]
	#name check
	if shapeName     in shapeDic:
		shapeDic[shapeName].append(transformName)
		worldMatDic[shapeName] += tempStringMatrix
	if shapeName not in shapeDic:
		shapeDic[shapeName] = [transformName]
		worldMatDic[shapeName] = tempStringMatrix
		dagPathArray.append(dagPath)

	iterDag.next()

	
#instance check...
cppInstanceStr = ""
for k in worldMatDic.keys():
	instanceList = shapeDic[k]
	instanceNum  = len(instanceList)
	
	worldMatDic[k] = "float worldMatrix[" + str(instanceNum*16) + "]={" + worldMatDic[k]
	worldMatDic[k] = worldMatDic[k].rpartition(",")[0] + "};\n\n"

# shape node check...
cppShapeStr = ""
nameSpaceStrList = []
for i in range(dagPathArray.length()):
	dagPathName = dagPathArray[i].fullPathName()
	shapeName     = dagPathName.rpartition("|")[2]
	instanceNum = len(shapeDic[shapeName])
	isInstance = False
	if instanceNum > 1:
		isInstance = True
	#cppShapeStr += MakeShapeNodeString(dagPathArray[i])
	eachCppShapeStr, nodeNameStr = MakeShapeNodeStringImp(dagPathArray[i],isInstance,instanceNum, worldMatDic[shapeName] )
	cppShapeStr += eachCppShapeStr
	nameSpaceStrList.append(nodeNameStr)

# CPP Scene Class...
cppSceneStr = """
struct RawMesh {
	unsigned int num_vertices;
	unsigned int num_face_indices;

	// vertex attributes...
	float* positions;
	float* normals;
	float* texcoords;
	uint16_t* indices;

	// instancing...
	bool has_instance;
	unsigned int num_instance;
	float* world_matricies;

	// texture name
	char* texture_fullpath_name;
	char* texture_name;

	// material setting
	bool use_alpha_test;
};
"""

cppSceneStr += """
class SceneMeshes{
public: 
	SceneMeshes(){}
	static RawMesh* raw_meshes;
	static const unsigned int sc_Num_Meshes = """

cppSceneStr += str(len(nameSpaceStrList)) + ";\n\n"



# init function
cppSceneStr += """
	static void Init(){
		raw_meshes = new RawMesh[sc_Num_Meshes];\n
"""

for i in range(len(nameSpaceStrList)):
	tempStr  = ""
	tempStr += "		raw_meshes["+ str(i) + "].num_vertices = "     + nameSpaceStrList[i] + "::num_vertices;\n"
	tempStr += "		raw_meshes["+ str(i) + "].num_face_indices = " + nameSpaceStrList[i] + "::num_face_indices;\n"
	tempStr += "		raw_meshes["+ str(i) + "].positions = "        + nameSpaceStrList[i] + "::positions;\n"		
	tempStr += "		raw_meshes["+ str(i) + "].normals = "          + nameSpaceStrList[i] + "::normals;\n"
	tempStr += "		raw_meshes["+ str(i) + "].texcoords = "          + nameSpaceStrList[i] + "::texcoords;\n"	
	tempStr += "		raw_meshes["+ str(i) + "].indices = "          + nameSpaceStrList[i] + "::indices;\n"	
	tempStr += "		raw_meshes["+ str(i) + "].has_instance = "          + nameSpaceStrList[i] + "::has_instance;\n"
	tempStr += "		raw_meshes["+ str(i) + "].num_instance = "          + nameSpaceStrList[i] + "::num_instance;\n"
	tempStr += "		raw_meshes["+ str(i) + "].world_matricies = "          + nameSpaceStrList[i] + "::worldMatrix;\n"	
	tempStr += "		raw_meshes["+ str(i) + "].texture_fullpath_name = " + nameSpaceStrList[i] + "::texture_fullpath_name;\n"
	tempStr += "		raw_meshes["+ str(i) + "].texture_name = "          + nameSpaceStrList[i] + "::texture_name;\n"	
	tempStr += "		raw_meshes["+ str(i) + "].use_alpha_test = "          + nameSpaceStrList[i] + "::use_alpha_test;\n"		
	tempStr += "\n"
	
	cppSceneStr += tempStr
cppSceneStr += "	}\n\n"

cppSceneStr += """
}; // struct SceneMeshes
RawMesh* SceneMeshes::raw_meshes;
"""


print cppSceneStr


# file writing...
output_file_object = open("C:\\Program Files (x86)\\SCE\\ORBIS SDKs\\1.600\\target\\samples\\sample_code\\graphics\\api_gnm\\Juji-Asahi\\assets\\test_body\\test.h", 'w')
output_file_object.write( "namespace ZCullTestScene{\n")

#output_file_object.write(cppTransformStr)
output_file_object.write(cppShapeStr)
output_file_object.write(cppSceneStr)
#output_file_object.write(cppInstanceStr)

output_file_object.write("\n} // namespace ZCullTestScene\n")
output_file_object.close()
	
