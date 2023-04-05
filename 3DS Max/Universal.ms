macroScript Copy_Objects_To_File 
Category:"Universal" 
toolTip:"Copy Objects to File"

(  
	thecopypastedir = getdir #autoback -- CHANGE THIS TO ANY FOLDER YOU WANT              
	thecopypastefile = "\pastefile.max" --this is the filename to save as...              
	thecopypastestring = thecopypastedir + thecopypastefile --this is the complete string              
	sel = getCurrentSelection()   
	-- Check for ForestPack and RailClone dependancies              
	iTooArr= #()  
	fn iTooProps =  
	(  
		start = iTooArr.count  
		rec=false  
		-- ForestPack              
		for i= 1 to iTooArr.count do  
		(  
			if classof iTooArr[i] == Forest_Pro then  
			(  
				select iTooArr[i]  
				macros.run "Forest Pack" "FP_MS_SelectAll"  
				forest = getCurrentSelection()   
				join sel forest  
			)  
		)  
		--RailClone              
		for i= 1 to iTooArr.count do  
		(  
			if (classof iTooArr[i] == RailClone_Pro) then  
			(  
				for j=1 to iTooArr[i].sobjnode.count do  
				(  
					if (iTooArr[i].sobjnode[j] !=undefined) then  
					(  
						select iTooArr[i].sobjnode[j]  
						temp = getCurrentSelection()   
						join sel temp  
					)  
				)  
				for j=1 to iTooArr[i].banode.count do  
				(  
					if (iTooArr[i].banode[j] !=undefined) then  
					(  
						select iTooArr[i].banode[j]  
						temp = getCurrentSelection()   
						join sel temp  
					)  
				)  
			)  
			select sel  
			for obj in $ do  
			if (classof obj == Forest_Pro or classof obj == RailClone_Pro) then  
			(  
				appendifunique iTooArr obj  
				if iTooArr.count> start then rec=true  
			)  
			if rec then iTooProps()   
		)  
	)  

	if $ != undefined do  
	(  
		for obj in $ do if (classof obj == Forest_Pro or classof obj == RailClone_Pro) then appendifunique iTooArr obj  
		iTooArr  
		sel = getCurrentSelection()   
		iTooProps()   
		selectmore sel  
		-- End of iToo stuff	              
		saveNodes $ thecopypastestring --this saves ("copies") the objects as a file              
	)
)

macroScript Paste_Objects_From_File 
Category:"Universal" 
toolTip:"Paste Objects from File"
(  
	thecopypastedir = getdir #autoback -- CHANGE THIS TO ANY FOLDER YOU WANT              
	thecopypastefile = "\pastefile.max" --this is the filename to save as...              
	thecopypastestring = thecopypastedir + thecopypastefile --this is the complete string              

	mergemaxfile (thecopypastedir + thecopypastefile) #select --this merges ("pastes") and selects objects from file
)

macroScript Create_Box
Category:"Universal" 
toolTip:"Create Box"

(  
	boxWidth = 100  
	boxHeight = 100  
	boxLength = 100  
	boxCenter = [0,0,0]  

	myBox = Box length:boxLength width:boxWidth height:boxHeight lengthsegs:1 widthsegs:1 heightsegs:1 pos:boxCenter
)

macroScript Create_Cylinder
Category:"Universal" 
toolTip:"Create Cylinder"

(  
	cylHeight = 100  
	cylRadius = 30  
	cylSides = 16  

	cylCenter = [0,0,0]  

	myCylinder = Cylinder height:cylHeight radius:cylRadius sides:cylSides pos:cylCenter

)

macroScript Create_Plane
Category:"Universal" 
toolTip:"Create Plane"

(  
	planeWidth = 100  
	planeLength = 100  
	 
	myPlane = Plane width:planeWidth length:planeLength mapcoords:true 

)

macroScript Create_Sphere
Category:"Universal" 
toolTip:"Create Sphere"

(  
	sphereRadius = 50  
	sphereSegments = 16  
	 
	mySphere = Sphere radius:sphereRadius segs:sphereSegments 
)

macroScript Detach_Objects
Category:"Universal" 
toolTip:"Detach Objects"

(  
	local start_objs = objects as array 

	fn reset_pivots coll = ( 
		centerPivot coll 
		worldAlignPivot coll 
		resetXForm coll 
		convertToPoly coll 
	) 
	 
	fn invert_set coll = ( 
		return (for obj in objects where findItem coll obj == 0 collect obj) 
	) 


	fn detach_elems = (  
		local the_objs = for obj in selection where superClassOf obj == geometryClass collect obj  
		for obj in the_objs do (  
			if convertToPoly obj != undefined do (  
				while polyOp.getNumFaces obj != 0 do (  
					local f_list = polyOp.getElementsUsingFace obj #{1}  
					local elem = polyOp.detachFaces obj f_list asNode:true  
				)  
				delete obj  
			)  
		)  
	)  
	 
	detach_elems()   
	reset_pivots (invert_set start_objs)

)

macroScript Drop_To_Floor
Category:"Universal" 
toolTip:"Drop To Floor"

(
	fn dropToZero objs =
	( 
		for obj in objs do 
		( 
			obj.pivot = [obj.center.x,obj.center.y,obj.min.z] 
			obj.pos.z = 0 -- set the object's Z position to 0 
		)
	)

	dropToZero selection -- drop all the selected objects to the Z position of 0
)

macroScript Select_Hard_Edges
Category:"Universal" 
toolTip:"Select Hard Edges"

(  
	obj = modPanel.getCurrentObject()   
	if obj != undefined then  
	(  
		case (classof obj) of  
		(  
			Edit_Poly:obj.setoperation #SelectHardEdges  
			Editable_Poly:obj.selectHardEdges()   
		)  
	)  
	
)

macroScript Make_Unique
Category:"Universal" 
toolTip:"Make Unique"

(  
	InstanceMgr.MakeObjectsUnique selection #prompt
)

macroScript Pivot_To_Bottom
Category:"Universal" 
toolTip:"Set Pivot To Bottom"

(  
	for obj in getCurrentSelection()  do obj.pivot = [obj.center.x,obj.center.y,obj.min.z]
)

macroScript Unasign_Material
Category:"Universal" 
toolTip:"Unasign Material"

(  
	for obj in getCurrentSelection()  do obj.material=undefined
)

macroScript Collapse_Selected
Category:"Universal" 
toolTip:"Collapse Selected"

(  
	Assets = #()  
	for o in selection do append Assets o  
	convertToPoly(Assets[1])  
	for i = 2 to Assets.count do  
	(  
		convertToPoly(Assets[i])  
		polyop.attach Assets[1] Assets[i]  
	)
	macros.run "PolyTools" "CenterPivot"
)

