import maya.cmds as cmds

def jfPar(offset):
	sel = cmds.ls(sl=1,sn=True)
	par = sel[0]
	axisR = []
	axisT = []
	axis = ['X', 'Y', 'Z']
	
	for child in sel[1:]:
		axisR = []
		axisT = []
		for axis in axis:
			if cmds.getAttr(child+'.rotate'+axis, l=True) == True:
					axisR.append(axis.lower())
			if cmds.getAttr(child+'.translate'+axis, l=True) == True:
					axisT.append(axis.lower())

		cmds.parentConstraint(par, child, mo=offset, st = axisT, sr = axisR)

def setColor(source, target):
	try:
		srcShape = cmds.listRelatives(source, shapes=True)[0]
	except:
		srcShape=source
	if not srcShape:
		srcColor = 0
	
	tgtShape = cmds.listRelatives(target, shapes=True)[0]
	##if overrideRGBColors is false, it's index	
	if cmds.getAttr(srcShape+'.overrideRGBColors') == False:
		srcColor = cmds.getAttr(srcShape+".overrideColor")
		colorType = 'index'
		cmds.setAttr(tgtShape + '.overrideRGBColors', 0)
	##if overrideRGBColors is true, it's RGB	
	if cmds.getAttr(srcShape+'.overrideRGBColors') == True:
		srcColor = cmds.getAttr(srcShape+".overrideColorRGB")
		colorType = 'RGB'
		cmds.setAttr(tgtShape + '.overrideRGBColors', 1)

	cmds.setAttr(tgtShape + ".overrideEnabled", 1)
	###if colorType == 0 that means it's an index color type which is pretty simple
	if colorType == 'index' :
		cmds.setAttr(tgtShape + ".overrideColor", srcColor)
	###if colorType == 0 that means it's an RGB color type which is more complicated
	if colorType == 'RGB' :
		rgb = ("R","G","B")
		#limit parColor to only 3 decimal places
		srcColor = tuple(map(lambda x: isinstance(x, float) and round (x, 3) or x, srcColor[0]))
		for channel, color in zip(rgb, srcColor):
			cmds.setAttr(tgtShape + ".overrideColor%s" %channel, color)

def setScale(source, target, scaleFactor):
	# scale it based on bounding box max and scale by the given scaleFactor
	try:
		srcShape = cmds.listRelatives(source, shapes=True)[0]
	except:
		srcShape = source
	selBBoxMax = cmds.getAttr(srcShape+'.boundingBoxMax')
	selBBoxMax = tuple(map(lambda x: isinstance(x, float) and round (x, 3) or x, selBBoxMax[0]))
	selBBoxMin = cmds.getAttr(srcShape+'.boundingBoxMin')
	selBBoxMin = tuple(map(lambda x: isinstance(x, float) and round (x, 3) or x, selBBoxMin[0]))
	# ...limit digits
	cmds.setAttr(target + '.localScaleX', ((selBBoxMax[0]-selBBoxMin[0])*scaleFactor))
	cmds.setAttr(target + '.localScaleY', ((selBBoxMax[1]-selBBoxMin[1])*scaleFactor))
	cmds.setAttr(target + '.localScaleZ', ((selBBoxMax[2]-selBBoxMin[2])*scaleFactor))


def jfPropLoc():
	# get selection
	sel = cmds.ls(sl=1,sn=True)
	propNS = 'propLoc'
	if not sel:
		cmds.warning('please select something')
	else:
		
		## first item is parent
		par = str(sel[0])
		#convert : into _ for breadcrumb of parent info
		parLN = '_'.join(par.split(':'))

		#get selCount
		selCount = len(sel)

		if selCount == 1:
						item = sel[0]												
						#if selCount is just one, do a simple setup
						print("soloRig")
						# create locator with offset group
						itemLoc = item +"_propLOC"
						itemLocGrp = '_'.join(item.split(':'))+"_propLOC_offsetGrp"
						cmds.spaceLocator(name=itemLoc)
						cmds.setAttr (itemLoc+ ".rotateOrder", 2)
						cmds.setAttr (itemLoc+ ".rotateOrder", k=True)
						
						
						# color it based on the target object
						setColor(item, itemLoc)
						# scale it based on bounding box max
						setScale(item, itemLoc, 1)

						# set up 'rig'
						cmds.group(name=itemLocGrp)
						cmds.matchTransform(itemLocGrp, item)

						## match translation and rotation of childLoc to child
						cmds.matchTransform(itemLoc, item)
						cmds.select(itemLoc, item)
						
						## constrain child to childLoc
						jfPar(False)
						cmds.select(itemLoc)

						# organize
						# check if cleanUp group exists
						if cmds.objExists('propLOC_TOOLS'):
								cmds.parent((itemLocGrp), 'propLOC_TOOLS')
						else:
								cmds.group(name='propLOC_TOOLS', empty=True)
								cmds.parent((itemLocGrp), 'propLOC_TOOLS')

		else:
				#else if selCount is more than 1
				## second item and byeond are children (prop)
				print("simple prop rig")
				selList = []
				for item in sel[1:]:
						child = item
						childNS = child.split(':')[0]
						childName= child.split(':')[1:]
						childLN = '_'.join(child.split(':'))
						if not childName:
								childName="noNS"
		
						# create locator with offset group
						childLoc =	item+'_to_' + parLN + "_propLOC"
						# childLocGrp = childLN+"_propLOC_offsetGrp_to_"+parLN
						childLocGrp = parLN + '_propLOC_offsetGrp'
						cmds.spaceLocator(name=childLoc)
						cmds.setAttr (childLoc+ ".rotateOrder", 2)
						cmds.setAttr (childLoc+ ".rotateOrder", k=True)
						
						
						
						# color it based on the target object
						setColor(sel[0], childLoc)
						# scale it based on bounding box max
						setScale(child, childLoc, 1)

						# organize
						if not cmds.objExists(childLocGrp):
							cmds.group(name=childLocGrp)

							## constrain childLoc group to par
							cmds.parentConstraint(par, childLocGrp)
						else:
							cmds.parent(childLoc, childLocGrp)

						## match translation and rotation of childLoc to child
						cmds.select(childLoc, child)
						mel.eval('matchTransform')
						## constrain child to childLoc
						jfPar(False)
						
						selList.append(childLoc)

						# organize
						# check if cleanUp group exists
						if cmds.objExists('propLOC_TOOLS'):
							try:
								cmds.parent((childLocGrp), 'propLOC_TOOLS')
							except:
								pass
						else:
								cmds.group(name='propLOC_TOOLS', empty=True)
								cmds.parent((childLocGrp), 'propLOC_TOOLS')
				cmds.select(selList)