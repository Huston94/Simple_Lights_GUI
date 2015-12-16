##############################
"""
Creator: 
- Huston Petty
- http://www.hustonpetty3d.com

Document: 
- simple_lights_GUI.py

Description:
- This tool displays all of the lights in your scene and only shows you the
- attributes you NEED to see. It will also give you access to all of your
- lights in one area without having to navigate around your scene and select on
- them or find them in your outliner.

How to Run:
- import Simple_Lights_GUI.simple_lights_GUI as hp
- reload(hp)
-
- hp.main_GUI(docked=False) #or hp.main_GUI(docked=False)

Video Tutorial:
- ______________________________

"""

import pymel.core as pm
import maya.utils as utils
import maya.mel as mel
import functools as fun
import os
import webbrowser
import re

if pm.pluginInfo("Mayatomr", query=True, loaded=True) != 1:
	pm.loadPlugin( "Mayatomr" )

pm.setAttr('defaultRenderGlobals.ren', 'mentalRay', type='string')

lights = pm.ls(lights=True)
ibl_list = pm.ls(type='mentalrayIblShape')
ibl_trans = pm.listRelatives(ibl_list, parent=True, fullPath=True)

########################################### GUI #################################################

def main_GUI(docked=False):
	global windowWidth, windowHeight, isDocked, windowName, dockedWindow, marginWidth

	isDocked = docked
	windowWidth = 390
	marginWidth = windowWidth-12
	windowHeight = 700
	windowLabel = 'HP3D | Simple Lights GUI'
	windowName = 'hp3dSimpleLightsWin'

	# Colors
	global primary_componentColor, secondary_componentColor, windowColor, disabled_componentColor, frameColor
	primary_componentColor = [.261, .380, .393]
	secondary_componentColor = [.175, .198, .200]
	windowColor = [.300, .305, .305]
	disabled_componentColor = [.322, .384, .388]
	frameColor = [primary_componentColor[0]/1.5, primary_componentColor[1]/1.5, primary_componentColor[2]/1.5]

	if pm.window(windowName, q=True, ex=True):
		pm.deleteUI(windowName)
	if pm.windowPref(windowName, q=True, ex=True):
		pm.windowPref(windowName, r=True)
	if pm.dockControl(windowName, q=True, ex=True):
		pm.deleteUI(windowName)

	global window_obj
	window_obj = pm.window(windowName, 
		title=windowLabel,
		w=windowWidth, h=windowHeight,
		mnb=False, mxb=False, 
		bgc=windowColor)

	pm.scrollLayout(w=windowWidth+40,)
	pm.columnLayout()
	pm.rowColumnLayout(nr=2, rh=[1, 7])
	pm.text(l='') # GUI SPACER 
	pm.rowColumnLayout(nc=3, cw=[[1, 7], [3, 7]])
	pm.text(l='') # GUI SPACER 
	all_sections()
	pm.text(l='') # GUI SPACER 

	if docked == False:
		window_obj.show()
	elif docked == True:
		allowedAreas = ['right', 'left']
		dockedWindow = pm.dockControl(windowName, l=windowLabel, a='right', con=window_obj, aa=allowedAreas, visible=True)

def all_sections():
	global main_layout
	main_layout = pm.rowColumnLayout()

	heading_area()
	pm.separator(w=marginWidth, h=14)
	info_area()
	pm.separator(w=marginWidth, h=14)
	lightCreation_area()
	pm.separator(w=marginWidth, h=14)

	global main_tabsLayout, lights_tab, lightTools_tab
	main_tabsLayout = pm.tabLayout() # [507, 330]  int(pm.window('MayaWindow', q=True, h=True)/2.69)

	lights_tab = pm.rowColumnLayout()
	lights_area()

	lightTools_tab = pm.rowColumnLayout()
	tools_area()

	pm.setParent(main_layout)
	# pm.text(l='', h=7)
	# pm.button(l='Close', w=marginWidth, h=25, bgc=primary_componentColor, c=closeWindow)

def heading_area():
	heading_layout = pm.rowColumnLayout(nc=3)

	image_btn = pm.iconTextButton(style='iconOnly', ann='www.hustonpetty3d.com', w=255, h=30, image1=get_icon_path('tool_brand_icon.png'), c=fun.partial(open_page, 'http://www.hustonpetty3d.com'))
	pm.text(l='', w=53) # GUI SPACER 
	pm.button(l='How To Use?', c=fun.partial(open_page, 'https://youtu.be/v0lNec7dnTE'), w=80, h=1, bgc=primary_componentColor, ann='Go to "How To Use" video') # NOT CONNECTED

	pm.setParent(main_layout)

def info_area():
	global info_layout
	info_layout = pm.rowColumnLayout(nc=5)

	leftInfo_area()
	pm.text(l='') # GUI SPACER
	pm.separator(horizontal=False, h=50, w=13)
	pm.text(l='') # GUI SPACER
	rightInfo_area()

def rightInfo_area():
	leftInfo_layout = pm.rowColumnLayout(nr=3)

	################## TEXT and MENU ####################
	leftTop_layout = pm.rowColumnLayout(nc=3, cal=[[1, 'left'], [3, 'right']])

	pm.text(l='Sort Method')
	pm.text(l='', w=35) # GUI SPACER
	global sortMethod_menu
	sortMethod_menu = pm.optionMenu(bgc=primary_componentColor, w=110, ann='Pick the way your lights are organized', cc=refreshWindow) # NOT CONNECTED
	pm.menuItem(l="Intensity (H-L)", ann='Sort lights based on intensity from Highest to Lowest')
	pm.menuItem(l="Intensity (L-H)", ann='Sort lights based on intensity from Lowest to Highest')
	pm.menuItem(l="Name (A-Z)", ann='Sort lights based on name from A to Z')
	pm.menuItem(l="Name (Z-A)", ann='Sort lights based on name from Z to A')
	pm.menuItem(l="Type", ann='Sort lights based on light type')
	pm.menuItem(l="----------", enable=False)
	pm.menuItem(l="Area", ann='Show only Area Lights')
	pm.menuItem(l="Spot", ann='Show only Spot Lights')
	pm.menuItem(l="Directional", ann='Show only Directional Lights')
	pm.menuItem(l="Point", ann='Show only Point Lights')
	pm.menuItem(l="IBL", ann='Show only IBL')

	pm.setParent(leftInfo_layout)

	################## SPACE ####################
	leftMid_layout = pm.rowColumnLayout(nc=1, h=3)
	pm.text(l='') # GUI SPACER
	pm.setParent(leftInfo_layout)

	################## TEXT and INTFIELD ####################
	leftBottom_layout = pm.rowColumnLayout(nc=3, cal=[[1, 'left'], [3, 'right']])
	
	pm.text(l='Lights In Scene:')
	pm.text(l='', w=77) # GUI SPACER
	global num_lights
	num_lights = pm.intField(editable=False, w=50, bgc=secondary_componentColor, ann='There are currently {0} lights in the scene'.format(len(lights)))

	pm.setParent(main_layout)

def leftInfo_area():
	rightInfo_layout = pm.rowColumnLayout(nr=1) # ral=[[1, 'right'], [2, 'right']]

	global refresh_btn
	refresh_btn = pm.button(l='Refresh', al='center', w=150, h=45, bgc=primary_componentColor, c=refreshWindow, ann='Refresh the interface when lights are deleted or not showing up') # NOT CONNECTED

	pm.setParent(info_layout)

def lightCreation_area():
	pm.text(l='Light Creation', al='center')
	buttons_layout = pm.rowColumnLayout(nc=5)
	pm.iconTextButton(style='iconOnly', w=windowWidth/5, h=50, c=fun.partial(createLight, 'area'), ann='Create a Mental Ray area light', image1=get_icon_path('arealight_icon.png'))
	pm.iconTextButton(style='iconOnly', w=windowWidth/5, h=50, c=fun.partial(createLight, 'spot'), ann='Create a spot light', image1=get_icon_path('spotlight_icon.png'))
	pm.iconTextButton(style='iconOnly', w=windowWidth/5, h=50, c=fun.partial(createLight, 'directional'), ann='Create a directional light', image1=get_icon_path('directionallight_icon.png'))
	pm.iconTextButton(style='iconOnly', w=windowWidth/5, h=50, c=fun.partial(createLight, 'point'), ann='Create a point light', image1=get_icon_path('pointlight_icon.png'))
	global ibl_btn
	ibl_btn = pm.iconTextButton(style='iconOnly', w=windowWidth/5, h=50, c=IBL_button, ann='Create an IBL', image1=get_icon_path('IBL_icon.png'))

	if ibl_list != []:
		ibl_btn.setImage1(get_icon_path('deleteIBL_icon.png'))

	pm.setParent(main_layout)

def lights_area():
	global lights_layout
	lights_layout = pm.rowColumnLayout(p=lights_tab)

	global lights
	lights = pm.ls(lights=True)
	ibl_list = pm.ls(type='mentalrayIblShape')
	num_lights.setValue(len(lights))
	num_lights.setAnnotation('There are currently {0} lights in the scene'.format(len(lights)))

	pm.text(l='Lights In Scene', al='center', w=marginWidth)
	pm.text(l='', h=7)
	for each in lightSorting(lights):
		name = pm.listRelatives(each, parent=True, fullPath=True)[0]
		lightType = pm.objectType(each)

		if lightType == 'areaLight': 
			light = AreaLight(name, lightType, each)
		elif lightType == 'spotLight': 
			light = SpotLight(name, lightType, each)
		elif lightType == 'directionalLight': 
			light = DirectionalLight(name, lightType, each)
		elif lightType == 'pointLight': 
			light = PointLight(name, lightType, each)

	if ibl_list != []:
		pm.separator(w=marginWidth, h=14)
		light = IBL_GUI(ibl_list[0])

	unsupported_lights = sortBy_unsupported(lights)
	if unsupported_lights != []:
		pm.separator(w=marginWidth, h=14)
		global unsupportedLights_layout
		unsupportedFrame_layout = pm.frameLayout(l='Unsupported Lights ({0})'.format(len(unsupported_lights)), cl=True, cll=True, w=marginWidth, bgc=frameColor, ann="The lights in this section are not supported by this GUI")
		unsupportedLights_layout = pm.columnLayout()

		for unsupported in unsupported_lights:
			unsup_name = pm.listRelatives(unsupported, parent=True, fullPath=True)[0]
			unsup_lightType = pm.objectType(unsupported)

			light = UnsupportedLight(unsupported, unsup_name, unsup_lightType)

		pm.setParent(lights_layout)

	pm.setParent(main_tabsLayout)
	main_tabsLayout.setTabLabel([lights_tab, 'Lights'])



def tools_area():
	# pm.text(l='', h=2) # GUI SPACER
	# pm.rowColumnLayout(nc=2)
	# pm.text(l='', w=120) # GUI SPACER
	# defaultGrey_box = pm.checkBox(l='Enable default lighting material')
	pm.setParent(lightTools_tab)
	pm.text(l='', h=2) # GUI SPACER

	multi_LightEditing()

	pm.setParent(main_tabsLayout)
	main_tabsLayout.setTabLabel([lightTools_tab, 'Tools'])

def multi_LightEditing():
	global multiLight_layout
	multiLightFrame_layout = pm.frameLayout(l='Multi-light Editing', cl=False, cll=True, w=marginWidth, bgc=frameColor, ann="Edit the attributes of multiple selected lights at the same time")
	multiLight_layout = pm.rowColumnLayout()

	multi_BasicSettings()
	multi_ShadowSettings()
	multi_MentalRaySettings()
	multi_SpotLightSettings()

	pm.setParent(lightTools_tab)

def multi_BasicSettings():
	# Basic Settings
	pm.text(l='', h=5)
	multi_nameField = pm.textFieldGrp('hp3dNameField', l='Name', text='', cw=[2, 150], cc=fun.partial(multi_nameChange, 'hp3dNameField'), fcc=True)

	pm.rowColumnLayout(nc=2)
	pm.text(l='Basic Settings', w=75, al='left', en=False)
	pm.separator(w=marginWidth-75, h=14)
	pm.setParent(multiLight_layout)

	multi_color = pm.colorSliderGrp('hp3dColorSlider', label='Color', rgb=(1, 1, 1), cw=[3, 20], dc=fun.partial(multi_colorChange, '.color', 'all', 'hp3dColorSlider'))
	multi_intensity = pm.floatSliderGrp('hp3dIntensitySlider', label='Intensity', field=True, v=1.000, fmx=1000000000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.intensity', 'all', 'hp3dIntensitySlider'))

	# pm.text(l='', h=3) # GUI SPACER
	pm.rowColumnLayout(nc=2)
	pm.text(l='', w=142) # GUI SPACER
	global multi_illDefault_box
	multi_illDefault_box = pm.checkBox(l='Illuminates by Default', v=1, cc=multi_illDefault)
	pm.setParent(multiLight_layout)

	pm.rowColumnLayout(nc=3)
	pm.text(l='', w=142) # GUI SPACER
	multi_emitDiff_box = pm.checkBox('hp3dEmitDiffCheckbox', l='Emit Diffuse', v=1, w=120, cc=fun.partial(multi_checkboxChange, '.emitDiffuse', 'all', 'hp3dEmitDiffCheckbox'))
	multi_emitSpec_box = pm.checkBox('hp3dEmitSpecCheckbox', l='Emit Specular', v=1, cc=fun.partial(multi_checkboxChange, '.emitSpecular', 'all', 'hp3dEmitSpecCheckbox'))
	pm.setParent(multiLight_layout)

	pm.rowColumnLayout(nc=3)
	pm.text(l='Decay Rate', w=140, al='right')
	pm.text(l='', w=3)
	multi_decayRate_menu = pm.optionMenu('hp3dDecayRateMenu', bgc=primary_componentColor, cc=fun.partial(multi_menuChange, '.decayRate', 'not directional', 'hp3dDecayRateMenu'))
	pm.menuItem(l='No Decay', da=0)
	pm.menuItem(l='Linear', da=1)
	pm.menuItem(l='Quadratic', da=2)
	pm.menuItem(l='Cubic', da=3)
	pm.setParent(multiLight_layout)

def multi_ShadowSettings():
	# Shadow Settings
	pm.rowColumnLayout(nc=2)
	pm.text(l='Shadow Settings', w=90, al='left', en=False)
	pm.separator(w=marginWidth-90, h=14)
	pm.setParent(multiLight_layout)

	multi_lightRadius = pm.floatSliderGrp('hp3dLightRadiusSlider', label='Light Radius', field=True, max=10.000, v=1.000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.lightRadius', 'spot & point', 'hp3dLightRadiusSlider'))
	multi_lightAngle = pm.floatSliderGrp('hp3dLightAngleSlider', label='Light Angle', field=True, max=10.000, v=1.000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.lightAngle', 'directionalLight', 'hp3dLightAngleSlider'))
	multi_shadowRays = pm.intSliderGrp('hp3dShadowRaysSlider', label='Shadow Rays', field=True, max=64, v=1, cw=[3, 20], dc=fun.partial(multi_intChange, '.shadowRays', 'all', 'hp3dShadowRaysSlider'))
	multi_rayDepth = pm.intSliderGrp('hp3dRayDepthSlider', label='Ray Depth Limit', field=True, max=15, v=3, cw=[3, 20], dc=fun.partial(multi_intChange, '.rayDepthLimit', 'all', 'hp3dRayDepthSlider'))
	pm.setParent(multiLight_layout)

def multi_MentalRaySettings():
	# Mental Ray Settings
	pm.rowColumnLayout(nc=2)
	pm.text(l='Mental Ray Settings', w=106, al='left', en=False)
	pm.separator(w=marginWidth-106, h=14)
	pm.setParent(multiLight_layout)

	pm.rowColumnLayout(nc=2)
	pm.text(l='', w=142) # GUI SPACER
	multi_MrAreaLight_box = pm.checkBox('hp3dUseShapeCheckbox', l='Use Light Shape', cc=fun.partial(multi_checkboxChange, '.areaLight', 'area & spot', 'hp3dUseShapeCheckbox'))
	pm.setParent(multiLight_layout)

	pm.rowColumnLayout(nc=3)
	pm.text(l='Type', w=140, al='right')
	pm.text(l='', w=3)
	multi_areaType_menu = pm.optionMenu('hp3dAreaTypeMenu', bgc=primary_componentColor, cc=fun.partial(multi_menuChange, '.areaType', 'area & spot', 'hp3dAreaTypeMenu'))
	pm.menuItem(l='Rectangle', da=0)
	pm.menuItem(l='Disc', da=1)
	pm.menuItem(l='Sphere', da=2)
	pm.menuItem(l='Cylinder', da=3)
	pm.menuItem(l='Custom', da=4)
	pm.setParent(multiLight_layout)

	multi_highSamples = pm.intFieldGrp('hp3dHighSamplesField', numberOfFields=1, label='High Samples', v1=8, cc=fun.partial(multi_samplesChange, 'highSamp'))
	multi_highSampLimit = pm.intFieldGrp('hp3dHighSampleLimitField', numberOfFields=1, label='High Sample Limit', v1=1, cc=fun.partial(multi_samplesChange, 'highSampLimit'))
	multi_lowSamples = pm.intFieldGrp('hp3dLowSamplesField', numberOfFields=1, label='Low Samples', v1=1, cc=fun.partial(multi_samplesChange, 'lowSamp'))
	pm.setParent(multiLight_layout)

def multi_SpotLightSettings():
	# Spot Light Settings
	pm.rowColumnLayout(nc=2)
	pm.text(l='Spot Light Settings', w=102, al='left', en=False)
	pm.separator(w=marginWidth-102, h=14)
	pm.setParent(multiLight_layout)

	multi_coneAngle = pm.floatSliderGrp('hp3dConeAngleSlider', label='Cone Angle', field=True, min=0.0057, max=179.9943, v=40.000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.coneAngle', 'spotLight', 'hp3dConeAngleSlider'))
	multi_penumbraAngle = pm.floatSliderGrp('hp3dPenumbraAngleSlider', label='Penumbra Angle', field=True, min=-10.000, max=10.000, v=0.000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.penumbraAngle', 'spotLight', 'hp3dPenumbraAngleSlider'))
	multi_dropoff = pm.floatSliderGrp('hp3dDropoffSlider', label='Dropoff', field=True, min=0, max=255.000, v=0.000, pre=3, cw=[3, 20], dc=fun.partial(multi_floatChange, '.dropoff', 'spotLight', 'hp3dDropoffSlider'))
	pm.setParent(multiLight_layout)


######################################### LIGHT SORTING #################################################

def lightSorting(lightList):
	sort_method = sortMethod_menu.getSelect()
	if sort_method == 1: # Intensity (A-Z)
		lightList = sortBy_intensity(lightList)
		return lightList
	elif sort_method == 2: # Intensity (Z-A)
		lightList = sortBy_intensity(lightList)
		lightList.reverse()
		return lightList
	elif sort_method == 3: # Name (A-Z)
		lightList.sort()
		return lightList
	elif sort_method == 4: # Name (Z-A)
		lightList.sort()
		lightList.reverse()
		return lightList
	elif sort_method == 5: # Type
		lightList = sortBy_type(lightList, 'all')
		return lightList
	elif sort_method == 7: # Area
		lightList = sortBy_type(lightList, 'areaLight')
		return lightList
	elif sort_method == 8: # Spot
		lightList = sortBy_type(lightList, 'spotLight')
		return lightList
	elif sort_method == 9: # Directional
		lightList = sortBy_type(lightList, 'directionalLight')
		return lightList
	elif sort_method == 10: # Point
		lightList = sortBy_type(lightList, 'pointLight')
		return lightList
	elif sort_method == 11: # IBL
		return []
	else:
		return lightList

def sortBy_unsupported(lightList):
	unsup_lights = []
	for each in lightList:
		if pm.objectType(each) == 'ambientLight' or pm.objectType(each) == 'volumeLight':
			unsup_lights.append(each)

	return unsup_lights

def sortBy_intensity(lightList):
	light_pairs = {}
	for light in lightList:
		light_intensity = light.getAttr('intensity')
		light_pairs[light] = light_intensity

	sorted_lights = []
	for each in sorted(light_pairs, key=light_pairs.get, reverse=True):
		sorted_lights.append(each)

	return sorted_lights

def sortBy_type(lightList, lightType):
	byArea = []
	bySpot = []
	byDirectional = []
	byPoint = []

	for each in lightList:
		eachType = pm.objectType(each)
		if eachType == 'areaLight':
			byArea.append(each)
		elif eachType == 'spotLight':
			bySpot.append(each)
		elif eachType == 'directionalLight':
			byDirectional.append(each)
		elif eachType == 'pointLight':
			byPoint.append(each)

	byArea.sort()
	bySpot.sort()
	byDirectional.sort()
	byPoint.sort()

	if lightType == 'all':
		return byArea + bySpot + byDirectional + byPoint
	elif lightType == 'areaLight':
		return byArea
	elif lightType == 'spotLight':
		return bySpot
	elif lightType == 'directionalLight':
		return byDirectional
	elif lightType == 'pointLight':
		return byPoint
	elif lightType == 'not directional':
		return byArea + bySpot + byPoint
	elif lightType == 'spot & point':
		return bySpot + byPoint
	elif lightType == 'area & spot':
		return byArea + bySpot

########################################### COMMANDS #################################################

def refreshWindow(*args):
	layout_name = pm.rowColumnLayout(lights_layout, q=True, fpn=True)
	utils.executeDeferred("import pymel.core as pm;pm.deleteUI('{0}')".format(layout_name))
	lights_area()

	ibl_list = pm.ls(type='mentalrayIblShape')
	if ibl_list != []:
		ibl_btn.setImage1(get_icon_path('deleteIBL_icon.png'))
	else:
		ibl_btn.setImage1(get_icon_path('IBL_icon.png'))

def closeWindow(*args):
	if not isDocked:
		pm.deleteUI(window_obj)
	elif isDocked:
		pm.deleteUI(dockedWindow)

def get_icon_path(icon, icon_folder='icons'):
	base_path = os.path.split(__file__)[0]
	return os.path.join(base_path, icon_folder, icon)

def open_page(site, *args):
	webbrowser.open(site)

def createLight(lightType, *args):
	if lightType == 'area':
		area_light = pm.shadingNode('areaLight', asLight=True)
		pm.setAttr(area_light + '.intensity', 500)
		pm.setAttr(area_light + '.decayRate', 2)
		pm.setAttr(area_light + '.areaLight', 1)
		pm.select(area_light)
	elif lightType == 'spot':
		spot_light = pm.shadingNode('spotLight', asLight=True)
		pm.setAttr(spot_light + '.intensity', 500)
		pm.setAttr(spot_light + '.decayRate', 2)
	elif lightType == 'directional':
		directional_light = pm.shadingNode('directionalLight', asLight=True)
	elif lightType == 'point':
		point_light = pm.shadingNode('pointLight', asLight=True)
		pm.setAttr(point_light + '.intensity', 500)
		pm.setAttr(point_light + '.decayRate', 2)

	refreshWindow(*args)

def IBL_button(*args):
	ibl_list = pm.ls(type='mentalrayIblShape')
	ibl_trans = pm.listRelatives(ibl_list, parent=True, fullPath=True)
	if ibl_list == []:
		# ibl_node = pm.createNode('mentalrayIblShape', name='mentalrayIblShape1')
		ibl_node = mel.eval('miCreateIbl;')
		ibl_btn.setImage1(get_icon_path('deleteIBL_icon.png'))
		ibl_list = pm.ls(type='mentalrayIblShape')
	else:
		pm.delete(ibl_trans[0])
		ibl_btn.setImage1(get_icon_path('IBL_icon.png'))
		ibl_list = pm.ls(type='mentalrayIblShape')

	refreshWindow(*args)

########################################### MULTI-CHANGE COMMANDS #################################################

def multi_nameChange(component, *args):
	sel_lights = pm.ls(sl=True, lights=True, dag=True)

	newName = pm.textFieldGrp(component, q=True, text=True)
	newName = re.sub('\s+', '_', newName)

	for light in sel_lights:
		trans = pm.listRelatives(light, parent=True, fullPath=True)[0]
		pm.rename(trans, newName)

	pm.textFieldGrp(component, e=True, text='')
	refreshWindow(*args)

def multi_illDefault(*args):
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	connections = pm.listConnections('defaultLightSet', d=False, s=True)

	for each in sel_lights:
		trans = pm.listRelatives(each, parent=True, fullPath=True)[0]
		if multi_illDefault_box.getValue() == 0 and trans in connections:
			defaultSet = pm.listConnections(trans, d=True, s=True, plugs=True)[0]
			pm.disconnectAttr(trans+'.instObjGroups[0]', defaultSet)

		elif multi_illDefault_box.getValue() == 1:
			pm.connectAttr(trans+'.instObjGroups',  'defaultLightSet.dagSetMembers', nextAvailable=True)

def multi_menuChange(attr, lightType, component, *args):
	value = pm.optionMenu(component, q=True, select=True)
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	new_list = sortBy_type(sel_lights, lightType)
	
	for each in new_list:
		pm.setAttr(each+attr, value-1)

def multi_checkboxChange(attr, lightType, component, *args):
	value = pm.checkBox(component, q=True, v=True)
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	new_list = sortBy_type(sel_lights, lightType)
	
	for each in new_list:
		pm.setAttr(each+attr, value)

def multi_colorChange(attr, lightType, component, *args):
	value = pm.colorSliderGrp(component, q=True, rgb=True)
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	new_list = sortBy_type(sel_lights, lightType)
	
	for each in new_list:
		pm.setAttr(each+attr, value)

def multi_floatChange(attr, lightType, component, *args):
	value = pm.floatSliderGrp(component, q=True, v=True)
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	new_list = sortBy_type(sel_lights, lightType)
	
	for each in new_list:
		pm.setAttr(each+attr, value)

def multi_intChange(attr, lightType, component, *args):
	value = pm.intSliderGrp(component, q=True, v=True)
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	new_list = sortBy_type(sel_lights, lightType)
	
	for each in new_list:
		pm.setAttr(each+attr, value)

def multi_samplesChange(attr, *args):
	sel_lights = pm.ls(sl=True, lights=True, dag=True)
	area_list = sortBy_type(sel_lights, 'areaLight')
	spot_list = sortBy_type(sel_lights, 'spotLight')
	
	if attr == 'highSamp':
		value = pm.intFieldGrp('hp3dHighSamplesField', q=True, v1=True)

		for each in area_list:
			pm.setAttr(each+'.areaHiSamples', value)
		for each in spot_list:
			pm.setAttr(each+'.areaSampling', value, value)
	elif attr == 'highSampLimit':
		value = pm.intFieldGrp('hp3dHighSampleLimitField', q=True, v1=True)

		for each in area_list:
			pm.setAttr(each+'.areaHiSampleLimit', value)
		for each in spot_list:
			pm.setAttr(each+'.areaLowLevel', value)
	elif attr == 'lowSamp':
		value = pm.intFieldGrp('hp3dLowSamplesField', q=True, v1=True)

		for each in area_list:
			pm.setAttr(each+'.areaLoSamples', value)
		for each in spot_list:
			pm.setAttr(each+'.areaLowSampling', value, value)

########################################### CLASSES #################################################

class BaseLight(object):
	def __init__(self, lightTransform, lightType, lightShape):
		self.lightLinked = pm.lightlink(query=True, shapes=False, light=lightShape)
		self.lightTransform = lightTransform
		self.lightType = lightType
		self.lightShape = lightShape

		self.lightFrame_layout = pm.frameLayout(l='{0} ({1})'.format(lightTransform, lightType), cl=True, cll=True, w=marginWidth, bgc=frameColor, ann="Settings for {0}".format(lightTransform), p=lights_layout)
		self.indivLight_layout = pm.columnLayout()

		self.warningCheck()

		pm.text(l='', h=5)
		self.nameField = pm.textFieldGrp(l='Name', text=lightTransform, cw=[2, 150], cc=self.nameChange, fcc=True)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Basic Settings', w=75, al='left', en=False)
		pm.separator(w=marginWidth-75, h=14)
		pm.setParent(self.indivLight_layout)

		pm.text(l='', h=2)

		pm.rowColumnLayout(nc=5)
		pm.button(l='Select', w=(marginWidth/3)-5, al='center', bgc=primary_componentColor, c=self.selectLight)
		pm.text(l='') # GUI SPACER
		pm.button(l='Delete', w=(marginWidth/3)-5, al='center', bgc=primary_componentColor, c=self.deleteLight)
		pm.text(l='') # GUI SPACER
		pm.button(l='Duplicate', w=(marginWidth/3)-5, al='center', bgc=primary_componentColor, c=self.duplicateLight)
		pm.setParent(self.indivLight_layout)
		pm.text(l='', h=2) # GUI SPACER

		pm.attrColorSliderGrp(at=lightShape+'.color', cw=[[2, 75], [3, 120]], sb=True)
		pm.attrFieldSliderGrp(at=lightShape+'.intensity', cw=[[2, 75], [3, 120]], hmb=False)

		# pm.text(l='', h=3) # GUI SPACER
		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.illDefault_box = pm.checkBox(l='Illuminates by Default', v=self.check_illumByDefault(), cc=self.illumDefaultCommand)
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=3)
		pm.text(l='', w=142) # GUI SPACER
		emitDif_box = pm.checkBox(l='Emit Diffuse', w=120)
		emitSpec_box = pm.checkBox(l='Emit Specular')
		pm.setParent(self.indivLight_layout)
		pm.connectControl(emitDif_box, lightShape+'.emitDiffuse')
		pm.connectControl(emitSpec_box, lightShape+'.emitSpecular')

		pm.setParent(lights_layout)

	def warningCheck(self):

		self.warning_layout = pm.columnLayout()

		# NON-IGNORABLE
		if pm.getAttr(self.lightShape+'.shadowColor') != (0, 0, 0):
			self.lightFrame_layout.setBackgroundColor([1, 0, 0])
			self.lightFrame_layout.setLabel('{0} ({1})  # ERRORS DETECTED'.format(self.lightTransform, self.lightType))
			self.warning_layout.setBackgroundColor([.7, 0, 0])

			self.shadowColor_layout = pm.rowColumnLayout(bgc =[1, 0, 0], nc=2, cal=[1, 'left'])
			pm.text(l='# WARNING: "Shadow Color" is not black', w=marginWidth-66)
			pm.button(l='Fix', w=50, ann='Change {0}\'s "Shadow Color" to black'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.fix_warningShape, '.shadowColor', [0,0,0], self.shadowColor_layout))
			pm.setParent(self.warning_layout)

		if pm.getAttr(self.lightShape+'.useRayTraceShadows') != 1:
			self.lightFrame_layout.setBackgroundColor([1, 0, 0])
			self.lightFrame_layout.setLabel('{0} ({1})  # ERRORS DETECTED'.format(self.lightTransform, self.lightType))
			self.warning_layout.setBackgroundColor([.7, 0, 0])

			self.rayTrace_layout =  pm.rowColumnLayout(bgc =[1, 0, 0], nc=2, cal=[1, 'left'])
			pm.text(l='# WARNING: "Use Ray Trace Shadows" is not on', w=marginWidth-66)
			pm.button(l='Fix', w=50, ann='Turn on {0}\'s "Use Ray Trace Shadows" option'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.fix_warningShape, '.useRayTraceShadows', 1, self.rayTrace_layout))
			pm.setParent(self.warning_layout)

		if self.lightType == 'areaLight' and pm.getAttr(self.lightShape+'.areaLight') != 1:
			self.lightFrame_layout.setBackgroundColor([1, 0, 0])
			self.lightFrame_layout.setLabel('{0} ({1})  # ERRORS DETECTED'.format(self.lightTransform, self.lightType))
			self.warning_layout.setBackgroundColor([.7, 0, 0])

			self.mrAreaLight_layout = pm.rowColumnLayout(bgc =[1, 0, 0], nc=2, cal=[1, 'left'])
			pm.text(l='# WARNING: Not a Mental Ray Light', w=marginWidth-66)
			pm.button(l='Fix', w=50, ann='Turn on {0}\'s "Use Light Shape" option'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.fix_warningShape, '.areaLight', 1, self.mrAreaLight_layout))
			pm.setParent(self.warning_layout)

		# IGNORABLE
		if pm.getAttr(self.lightTransform+'.visibility') != 1:
			self.lightFrame_layout.setBackgroundColor([1, 0, 0])
			self.lightFrame_layout.setLabel('{0} ({1})  # ERRORS DETECTED'.format(self.lightTransform, self.lightType))

			self.visibility_layout = pm.rowColumnLayout(bgc =[1, .916, .4], nc=4, cal=[1, 'left'])
			pm.text(l='# WARNING: Light is not visible in scene', w=marginWidth-120)
			pm.button(l='Ignore', w=50, ann='Turn on {0}\'s visibility'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.ignore_warning, self.visibility_layout))
			pm.text(l='', w=2) # GUI SPACER
			pm.button(l='Fix', w=50, ann='Turn on {0}\'s visibility'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.fix_warningTrans, '.visibility', 1, self.visibility_layout))
			pm.setParent(self.warning_layout)

		if pm.getAttr(self.lightShape+'.decayRate') != 2 and self.lightType != 'directionalLight':
			self.lightFrame_layout.setBackgroundColor([1, 0, 0])
			self.lightFrame_layout.setLabel('{0} ({1})  # ERRORS DETECTED'.format(self.lightTransform, self.lightType))

			self.decayRateWarning_layout =  pm.rowColumnLayout(bgc =[1, .916, .4], nc=4, cal=[1, 'left'])
			pm.text(l='# WARNING: "Decay Rate" is not Quadratic', w=marginWidth-120)
			pm.button(l='Ignore', w=50, ann='Turn on {0}\'s visibility'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.ignore_warning, self.decayRateWarning_layout))
			pm.text(l='', w=2) # GUI SPACER
			pm.button(l='Fix', w=50, ann='Turn on {0}\'s visibility'.format(self.lightTransform), bgc=primary_componentColor, 
				c=fun.partial(self.fix_warningShape, '.decayRate', 2, self.decayRateWarning_layout))
			pm.setParent(self.warning_layout)

		self.delWarningLayout()

		pm.setParent(self.indivLight_layout)

	def fix_warningTrans(self, attr, val, layout, *args):
		pm.setAttr(self.lightTransform+attr, val)
		pm.deleteUI(layout)
		self.delWarningLayout()

	def fix_warningShape(self, attr, val, layout, *args):
		pm.setAttr(self.lightShape+attr, val)
		pm.deleteUI(layout)
		self.delWarningLayout()
	
	def ignore_warning(self, layout, *args):
		pm.deleteUI(layout)
		self.delWarningLayout()

	def delWarningLayout(self):
		if pm.columnLayout(self.warning_layout, nch=True, q=True) == 0:
			pm.deleteUI(self.warning_layout)
			self.lightFrame_layout.setBackgroundColor(frameColor)
			self.lightFrame_layout.setLabel('{0} ({1})'.format(self.lightTransform, self.lightType))

	def nameChange(self, *args):
		newName = self.nameField.getText()
		newName = re.sub('\s+', '_', newName)
		pm.rename(self.lightTransform, newName)
		refreshWindow(*args)

	def selectLight(self, *args):
		pm.select(self.lightTransform)

	def deleteLight(self, *args):
		pm.delete(self.lightTransform)
		refreshWindow(*args)

	def duplicateLight(self, *args):
		pm.duplicate(self.lightTransform, rr=True)
		pm.xform(self.lightTransform, t=[0, 0, 3], r=True)
		refreshWindow(*args)

	def check_illumByDefault(self):
		connections = pm.listConnections('defaultLightSet', d=False, s=True)
		if self.lightTransform in connections:
			return 1
		elif self.lightTransform not in connections:
			return 0

	def illumDefaultCommand(self, *args):
		connections = pm.listConnections('defaultLightSet', d=False, s=True)
		if self.illDefault_box.getValue() == 0 and self.lightTransform in connections:
			defaultSet = pm.listConnections(self.lightTransform, d=True, s=False, plugs=True)[0]
			pm.disconnectAttr(self.lightTransform+'.instObjGroups[0]', defaultSet)

		elif self.illDefault_box.getValue() == 1:
			pm.connectAttr(self.lightTransform+'.instObjGroups',  'defaultLightSet.dagSetMembers', nextAvailable=True)

class AreaLight(BaseLight):
	def __init__(self, lightTransform, lightType, lightShape):
		super(AreaLight, self).__init__(lightTransform, lightType, lightShape)
		pm.setParent(self.indivLight_layout)
		
		pm.rowColumnLayout(nc=3)
		pm.text(l='Decay Rate', w=140, al='right')
		pm.text(l='', w=3)
		decayRate_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='No Decay', da=0)
		pm.menuItem(l='Linear', da=1)
		pm.menuItem(l='Quadratic', da=2)
		pm.menuItem(l='Cubic', da=3)
		pm.connectControl(decayRate_menu, lightShape+'.decayRate')
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Shadow Settings', w=90, al='left', en=False)
		pm.separator(w=marginWidth-90, h=14)
		pm.setParent(self.indivLight_layout)

		self.shadowRays_slide = pm.attrFieldSliderGrp(at=lightShape+'.shadowRays', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.rayDepthLimit', cw=[[2, 75], [3, 120]], hmb=False)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Mental Ray Settings', w=106, al='left', en=False)
		pm.separator(w=marginWidth-106, h=14)
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.areaLight_box = pm.checkBox(l='Use Light Shape', cc=self.MR_settings_enable)
		pm.connectControl(self.areaLight_box, lightShape+'.areaLight')
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=3)
		self.areaType_text = pm.text(l='Type', w=140, al='right')
		pm.text(l='', w=3)
		self.areaType_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='Rectangle', da=0)
		pm.menuItem(l='Disc', da=1)
		pm.menuItem(l='Sphere', da=2)
		pm.menuItem(l='Cylinder', da=3)
		pm.menuItem(l='Custom', da=4)
		pm.connectControl(self.areaType_menu, lightShape+'.areaType')
		pm.setParent(self.indivLight_layout)

		self.highSamples = pm.intFieldGrp(numberOfFields=1, label='High Samples')
		self.highSampLimit = pm.intFieldGrp(numberOfFields=1, label='High Sample Limit')
		self.lowSamples = pm.intFieldGrp(numberOfFields=1, label='Low Samples')
		pm.connectControl(self.highSamples, lightShape+'.areaHiSamples', index=2)
		pm.connectControl(self.highSampLimit, lightShape+'.areaHiSampleLimit', index=2)
		pm.connectControl(self.lowSamples, lightShape+'.areaLoSamples', index=2)
		# self.highSamples = pm.attrFieldGrp(l='High Samples', at=lightShape+'.areaHiSamples')
		# self.highSampLimit = pm.attrFieldGrp(l='High Sample Limit', at=lightShape+'.areaHiSampleLimit')
		# self.lowSamples = pm.attrFieldGrp(l='Low Samples', at=lightShape+'.areaLoSamples')

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.visibility_box = pm.checkBox(l='Visible', cc=self.MR_settings_enable)
		pm.connectControl(self.visibility_box, lightShape+'.areaVisible')
		pm.setParent(self.indivLight_layout)
		self.shapeIntensity = pm.attrFieldSliderGrp(l='Shape Intensity', at=lightShape+'.areaShapeIntensity', cw=[[2, 75], [3, 120]], hmb=False)
		self.MR_settings_enable()

		pm.setParent(lights_layout)

	def MR_settings_enable(self, *args):
		if self.visibility_box.getValue() == 1:
			self.shapeIntensity.setEnable(1)
		elif self.visibility_box.getValue() == 0:
			self.shapeIntensity.setEnable(0)

		if self.areaLight_box.getValue() == 0:
			self.shadowRays_slide.setEnable(1)
			self.highSamples.setEnable(0)
			self.areaType_menu.setEnable(0)
			self.areaType_menu.setBackgroundColor(disabled_componentColor)
			self.areaType_text.setEnable(0)
			self.highSampLimit.setEnable(0)
			self.lowSamples.setEnable(0)
			self.visibility_box.setEnable(0)
			self.shapeIntensity.setEnable(0)
		elif self.areaLight_box.getValue() == 1:
			self.shadowRays_slide.setEnable(0)
			self.highSamples.setEnable(1)
			self.areaType_menu.setEnable(1)
			self.areaType_menu.setBackgroundColor(primary_componentColor)
			self.areaType_text.setEnable(1)
			self.highSampLimit.setEnable(1)
			self.lowSamples.setEnable(1)
			self.visibility_box.setEnable(1)

class SpotLight(BaseLight):
	def __init__(self, lightTransform, lightType, lightShape):
		super(SpotLight, self).__init__(lightTransform, lightType, lightShape)
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=3)
		pm.text(l='Decay Rate', w=140, al='right')
		pm.text(l='', w=3)
		decayRate_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='No Decay', da=0)
		pm.menuItem(l='Linear', da=1)
		pm.menuItem(l='Quadratic', da=2)
		pm.menuItem(l='Cubic', da=3)
		pm.connectControl(decayRate_menu, lightShape+'.decayRate')
		pm.setParent(self.indivLight_layout)

		pm.attrFieldSliderGrp(at=lightShape+'.coneAngle', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.penumbraAngle', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.dropoff', cw=[[2, 75], [3, 120]], hmb=False)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Shadow Settings', w=90, al='left', en=False)
		pm.separator(w=marginWidth-90, h=14)
		pm.setParent(self.indivLight_layout)

		pm.attrFieldSliderGrp(at=lightShape+'.lightRadius', cw=[[2, 75], [3, 120]], hmb=False)
		self.shadowRays_slide = pm.attrFieldSliderGrp(at=lightShape+'.shadowRays', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.rayDepthLimit', cw=[[2, 75], [3, 120]], hmb=False)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Mental Ray Settings', w=106, al='left', en=False)
		pm.separator(w=marginWidth-106, h=14)
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.areaLight_box = pm.checkBox(l='Area Light', cc=self.MR_settings_enable)
		pm.connectControl(self.areaLight_box, lightShape+'.areaLight')
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=3)
		self.areaType_text = pm.text(l='Type', w=140, al='right')
		pm.text(l='', w=3)
		self.areaType_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='Rectangle', da=0)
		pm.menuItem(l='Disc', da=1)
		pm.menuItem(l='Sphere', da=2)
		pm.menuItem(l='Cylinder', da=3)
		pm.menuItem(l='Custom', da=4)
		pm.connectControl(self.areaType_menu, lightShape+'.areaType')
		pm.setParent(self.indivLight_layout)

		self.highSamples = pm.intFieldGrp(numberOfFields=2, label='High Samples')
		self.highSampLimit = pm.intFieldGrp(numberOfFields=1, label='High Sample Limit')
		self.lowSamples = pm.intFieldGrp(numberOfFields=2, label='Low Samples')
		pm.connectControl(self.highSamples, lightShape+'.areaSamplingU', index=2)
		pm.connectControl(self.highSamples, lightShape+'.areaSamplingV', index=3)
		pm.connectControl(self.highSampLimit, lightShape+'.areaLowLevel', index=2)
		pm.connectControl(self.lowSamples, lightShape+'.areaLowSamplingU', index=2)
		pm.connectControl(self.lowSamples, lightShape+'.areaLowSamplingV', index=3)
		# self.highSamples = pm.attrFieldGrp(l='High Samples', at=lightShape+'.areaSampling')
		# self.highSampLimit = pm.attrFieldGrp(l='High Sample Limit', at=lightShape+'.areaLowLevel')
		# # self.lowSamples = pm.attrFieldGrp(l='Low Samples', at=lightShape+'.areaLowSampling')

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.visibility_box = pm.checkBox(l='Visible')
		pm.connectControl(self.visibility_box, lightShape+'.areaVisible')
		pm.setParent(self.indivLight_layout)
		self.MR_settings_enable()

		pm.rowColumnLayout(nc=2)
		pm.text(l='Barn Doors Settings', w=106, al='left', en=False)
		pm.separator(w=marginWidth-106, h=14)
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.barnDoors_box = pm.checkBox(l='Barn Doors', cc=self.barnDoors_enable)
		pm.connectControl(self.barnDoors_box, lightShape+'.barnDoors')
		pm.setParent(self.indivLight_layout)

		self.leftBarn = pm.attrFieldSliderGrp(at=lightShape+'.leftBarnDoor', cw=[[2, 75], [3, 120]])
		self.rightBarn = pm.attrFieldSliderGrp(at=lightShape+'.rightBarnDoor', cw=[[2, 75], [3, 120]])
		self.topBarn = pm.attrFieldSliderGrp(at=lightShape+'.topBarnDoor', cw=[[2, 75], [3, 120]])
		self.bottomBarn = pm.attrFieldSliderGrp(at=lightShape+'.bottomBarnDoor', cw=[[2, 75], [3, 120]])
		self.barnDoors_enable()

		pm.setParent(lights_layout)

	def barnDoors_enable(self, *args):
		if self.barnDoors_box.getValue() == 0:
			self.leftBarn.setEnable(0)
			self.rightBarn.setEnable(0)
			self.topBarn.setEnable(0)
			self.bottomBarn.setEnable(0)
		elif self.barnDoors_box.getValue() == 1:
			self.leftBarn.setEnable(1)
			self.rightBarn.setEnable(1)
			self.topBarn.setEnable(1)
			self.bottomBarn.setEnable(1)

	def MR_settings_enable(self, *args):
		if self.areaLight_box.getValue() == 0:
			self.shadowRays_slide.setEnable(1)
			self.highSamples.setEnable(0)
			self.areaType_menu.setEnable(0)
			self.areaType_menu.setBackgroundColor(disabled_componentColor)
			self.areaType_text.setEnable(0)
			self.highSampLimit.setEnable(0)
			self.lowSamples.setEnable(0)
			self.visibility_box.setEnable(0)
		elif self.areaLight_box.getValue() == 1:
			self.shadowRays_slide.setEnable(0)
			self.highSamples.setEnable(1)
			self.areaType_menu.setEnable(1)
			self.areaType_menu.setBackgroundColor(primary_componentColor)
			self.areaType_text.setEnable(1)
			self.highSampLimit.setEnable(1)
			self.lowSamples.setEnable(1)
			self.visibility_box.setEnable(1)

class DirectionalLight(BaseLight):
	def __init__(self, lightTransform, lightType, lightShape):
		super(DirectionalLight, self).__init__(lightTransform, lightType, lightShape)
		pm.setParent(self.indivLight_layout)
		
		pm.rowColumnLayout(nc=2)
		pm.text(l='Shadow Settings', w=90, al='left', en=False)
		pm.separator(w=marginWidth-90, h=14)
		pm.setParent(self.indivLight_layout)

		pm.attrFieldSliderGrp(at=lightShape+'.lightAngle', cw=[[2, 75], [3, 120]], hmb=False)
		self.shadowRays_slide = pm.attrFieldSliderGrp(at=lightShape+'.shadowRays', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.rayDepthLimit', cw=[[2, 75], [3, 120]], hmb=False)

		pm.setParent(lights_layout)

class PointLight(BaseLight):
	def __init__(self, lightTransform, lightType, lightShape):
		super(PointLight, self).__init__(lightTransform, lightType, lightShape)
		pm.setParent(self.indivLight_layout)
		
		pm.rowColumnLayout(nc=3)
		pm.text(l='Decay Rate', w=140, al='right')
		pm.text(l='', w=3)
		decayRate_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='No Decay', da=0)
		pm.menuItem(l='Linear', da=1)
		pm.menuItem(l='Quadratic', da=2)
		pm.menuItem(l='Cubic', da=3)
		pm.connectControl(decayRate_menu, lightShape+'.decayRate')
		pm.setParent(self.indivLight_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Shadow Settings', w=90, al='left', en=False)
		pm.separator(w=marginWidth-90, h=14)
		pm.setParent(self.indivLight_layout)

		pm.attrFieldSliderGrp(at=lightShape+'.lightRadius', cw=[[2, 75], [3, 120]], hmb=False)
		self.shadowRays_slide = pm.attrFieldSliderGrp(at=lightShape+'.shadowRays', cw=[[2, 75], [3, 120]], hmb=False)
		pm.attrFieldSliderGrp(at=lightShape+'.rayDepthLimit', cw=[[2, 75], [3, 120]], hmb=False)

		pm.setParent(lights_layout)

class IBL_GUI(BaseLight):
	def __init__(self, shape):
		self.lightShape = shape
		self.lightTransform = pm.listRelatives(self.lightShape, parent=True, fullPath=True)[0]

		self.existingPath = pm.getAttr(self.lightShape+'.texture')
		if self.existingPath == None:
			self.existingPath = ''

		iblFrame_layout = pm.frameLayout(l='{0} ({1})'.format(self.lightTransform, 'mentalrayIbl'), cl=True, cll=True, w=marginWidth, bgc=frameColor, ann="Settings for {0}".format(self.lightTransform), p=lights_layout)
		ibl_layout = pm.columnLayout()

		pm.text(l='', h=5)
		self.nameField = pm.textFieldGrp(l='Name', text=self.lightTransform, cw=[2, 150], cc=self.nameChange, fcc=True)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Basic Settings', w=75, al='left', en=False)
		pm.separator(w=marginWidth-75, h=14)
		pm.setParent(ibl_layout)
		
		pm.rowColumnLayout(nc=3)
		pm.text(l='Mapping', w=140, al='right')
		pm.text(l='', w=3)
		mapping_menu = pm.optionMenu(bgc=primary_componentColor)
		pm.menuItem(l='Spherical', da=0)
		pm.menuItem(l='Angular', da=1)
		pm.connectControl(mapping_menu, self.lightShape+'.mapping')
		pm.setParent(ibl_layout)

		pm.rowColumnLayout(nc=3)
		pm.text(l='Type', w=140, al='right')
		pm.text(l='', w=3)
		self.type_menu = pm.optionMenu(bgc=primary_componentColor, cc=self.iblSettings_enabled)
		pm.menuItem(l='Image File', da=0)
		pm.menuItem(l='Texture', da=1)
		pm.connectControl(self.type_menu, self.lightShape+'.type')
		pm.setParent(ibl_layout)

		pm.text(l='', h=2)
		pm.rowColumnLayout(nc=2, cw=[2, 18])
		self.ibl_filePath = pm.textFieldGrp(label='Image Name', text=self.existingPath, cw=[2, 170], cc=self.updatePath)
		self.nav_btn = pm.iconTextButton(style='iconOnly', c=self.browse_btn, ann='Browse for file', image1=get_icon_path('folder_icon.png'))
		pm.setParent(ibl_layout)

		self.texture = pm.attrColorSliderGrp(l='Texture', at=self.lightShape+'.color', cw=[[2, 75], [3, 120]], sb=True)

		pm.rowColumnLayout(nc=2)
		pm.text(l='Render Stats', w=69, al='left', en=False)
		pm.separator(w=marginWidth-69, h=14)
		pm.setParent(ibl_layout)

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		primVis_box = pm.checkBox(l='Primary Visibilty')
		pm.connectControl(primVis_box, self.lightShape+'.primaryVisibility')

		pm.text(l='', w=142) # GUI SPACER
		visEnv_box = pm.checkBox(l='Visible as Environment')
		pm.connectControl(visEnv_box, self.lightShape+'.visibleInEnvironment')

		pm.text(l='', w=142) # GUI SPACER
		visRefl_box = pm.checkBox(l='Visible In Secondary Reflections')
		pm.connectControl(visRefl_box, self.lightShape+'.visibleInReflections')

		pm.text(l='', w=142) # GUI SPACER
		visRefr_box = pm.checkBox(l='Visible In Refractions')
		pm.connectControl(visRefr_box, self.lightShape+'.visibleInRefractions')

		pm.text(l='', w=142) # GUI SPACER
		visFG_box = pm.checkBox(l='Visible In Final Gather')
		pm.connectControl(visFG_box, self.lightShape+'.visibleInFinalGather')

		pm.text(l='', w=142) # GUI SPACER
		self.envColorFX_box = pm.checkBox(l='Adjust Environment Color Effects', cc=self.iblSettings_enabled)
		pm.connectControl(self.envColorFX_box, self.lightShape+'.overrideEnvColorFx')
		
		pm.text(l='', w=142) # GUI SPACER
		self.envInvert_box = pm.checkBox(l='Invert')
		pm.connectControl(self.envInvert_box, self.lightShape+'.envInvert')
		pm.setParent(ibl_layout)

		self.envColorGain = pm.attrColorSliderGrp(l='Color Gain', at=self.lightShape+'.envColorGain', cw=[[2, 75], [3, 120]], sb=True)
		self.envColorOffset = pm.attrColorSliderGrp(l='Color Offset', at=self.lightShape+'.envColorOffset', cw=[[2, 75], [3, 120]], sb=True)

		pm.rowColumnLayout(nc=2)
		pm.text(l='', w=142) # GUI SPACER
		self.fgColorFX_box = pm.checkBox(l='Adjust Final Gather Color Effects', cc=self.iblSettings_enabled)
		pm.connectControl(self.fgColorFX_box, self.lightShape+'.overrideFgColorFx')
		
		pm.text(l='', w=142) # GUI SPACER
		self.fgInvert_box = pm.checkBox(l='Invert')
		pm.connectControl(self.fgInvert_box, self.lightShape+'.fgInvert')
		pm.setParent(ibl_layout)

		self.fgColorGain = pm.attrColorSliderGrp(l='Color Gain', at=self.lightShape+'.fgColorGain', cw=[[2, 75], [3, 120]], sb=True)
		self.fgColorOffset = pm.attrColorSliderGrp(l='Color Offset', at=self.lightShape+'.fgColorOffset', cw=[[2, 75], [3, 120]], sb=True)

		self.iblSettings_enabled()
		pm.setParent(lights_layout)

	def browse_btn(self, *args):
		try:
			self.imagePath = pm.fileDialog2(fileMode=1)[0]
		except TypeError:
			self.imagePath = pm.getAttr(self.lightShape+'.texture')
		
		self.ibl_filePath.setText(self.imagePath)
		pm.setAttr(self.lightShape+'.texture', self.imagePath, type="string")

	def updatePath(self, *args):
		newPath = self.ibl_filePath.getText()
		pm.setAttr(self.lightShape+'.texture', newPath, type="string")

	def iblSettings_enabled(self, *args):
		iblType = self.type_menu.getSelect()
		envColorFX = self.envColorFX_box.getValue()
		fgColorFX = self.fgColorFX_box.getValue()

		if iblType == 1:
			self.ibl_filePath.setEnable(1)
			self.nav_btn.setEnable(1)
			self.texture.setEnable(0)
		elif iblType == 2:
			self.ibl_filePath.setEnable(0)
			self.nav_btn.setEnable(0)
			self.texture.setEnable(1)

		if envColorFX == 0:
			self.envInvert_box.setEnable(0)
			self.envColorGain.setEnable(0)
			self.envColorOffset.setEnable(0)
		elif envColorFX == 1:
			self.envInvert_box.setEnable(1)
			self.envColorGain.setEnable(1)
			self.envColorOffset.setEnable(1)

		if fgColorFX == 0:
			self.fgInvert_box.setEnable(0)
			self.fgColorGain.setEnable(0)
			self.fgColorOffset.setEnable(0)
		elif fgColorFX == 1:
			self.fgInvert_box.setEnable(1)
			self.fgColorGain.setEnable(1)
			self.fgColorOffset.setEnable(1)

class UnsupportedLight(object):
	def __init__(self, shape, trans, lightType):
		self.lightShape = shape
		self.lightTransform = trans
		self.lightType = lightType

		indivUnsupported_layout = pm.rowColumnLayout(nc=1, cal=[1, 'left'])
		pm.text(l="# {0} ({1}) not supported in this window".format(self.lightTransform, self.lightType), w=marginWidth)
		# pm.button(l='Delete', w=50, ann='Change {0}\'s "Shadow Color" to black'.format(self.lightTransform), bgc=primary_componentColor, c=self.fix_shadowColor)
		pm.setParent(unsupportedLights_layout)
		pm.separator(w=marginWidth, h=14)









