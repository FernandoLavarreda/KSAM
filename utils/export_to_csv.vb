'Fernando Lavarreda
'Export Inventor sketch to csv, by diffault pick the first sketch
Sub Main()
    Dim partDoc As PartDocument
    partDoc = ThisApplication.ActiveDocument
	Dim oFileDlg As FileDialog
    Call ThisApplication.CreateFileDialog(oFileDlg)
    oFileDlg.Filter = "CSV (*.csv;*.txt)|*.csv;*.txt|All Files (*.*)|*.*"
	oFileDlg.DialogTitle = "Save Info"
    oFileDlg.InitialDirectory = "C:\Documents"
	oFileDlg.CancelError = True
	On Error Resume Next
	oFileDlg.ShowSave
	If Err.Number
		Exit Sub
	End If
	filePath = oFileDlg.FileName
	Dim sketch As Sketch
    input_ = InputBox("Select a sketch to process: ", "Sketch", "1")
	sketch_num = 1
	If IsNumeric(input_)
		sketch_num = CInt(input_)
		If Not sketch_num <= partDoc.ComponentDefinition.Sketches.Count
			sketch_num = 1
		End If
	End If 
	save_ = Applitcation
    sketch = partDoc.ComponentDefinition.Sketches.Item(sketch_num)

    Dim coordinateData As String
    coordinateData = "X, Y" & vbCrLf
    
    Dim entity As SketchEntity
    For Each entity In sketch.SketchEntities
        If TypeOf entity Is SketchLine Then
			coordinateData = coordinateData & "New Line" & vbCrLf
            Dim line As SketchLine
            line = entity
            coordinateData = coordinateData & line.StartSketchPoint.Geometry.X & ", " & line.StartSketchPoint.Geometry.Y & vbCrLf
            coordinateData = coordinateData & line.EndSketchPoint.Geometry.X & ", " & line.EndSketchPoint.Geometry.Y & vbCrLf
        ElseIf TypeOf entity Is SketchArc Then
			coordinateData = coordinateData & "New Arc" & vbCrLf
			Dim arc As SketchArc
            arc = entity
			startPoint = arc.StartSketchPoint.Geometry
    		endPoint = arc.EndSketchPoint.Geometry
			centerPoint = arc.CenterSketchPoint.Geometry
    		radius = arc.Radius
            
			totalAngle = arc.SweepAngle
			differential = totalAngle / 100
			For angle = arc.StartAngle + differential To arc.StartAngle + totalAngle Step differential
				x = centerPoint.X + radius * Math.Cos(angle)
        		y = centerPoint.Y + radius * Math.Sin(angle)
				coordinateData = coordinateData & x & ", " & y & vbCrLf
			Next 
        	coordinateData = coordinateData & endPoint.X & ", " & endPoint.Y & vbCrLf
		ElseIf TypeOf entity Is SketchCircle Then
			coordinateData = coordinateData & "New Circle" & vbCrLf
			Dim circle As SketchCircle
            circle = entity
			radius = circle.Radius
			center = circle.CenterSketchPoint.Geometry
			stepSize = 0.01
			For angle = 0 To PI Step stepSize
				x = center.X + radius * Math.Cos(angle)
        		y = center.Y + radius * Math.Sin(angle)
				coordinateData = coordinateData & x & ", " & y & vbCrLf
			Next
		ElseIf TypeOf entity Is SketchSpline
			coordinateData = coordinateData & "New Spline" & vbCrLf
			Dim spline As SketchSpline
			spline = entity
			stepSize = 0.01
			
			Dim evaluator As Curve2dEvaluator
    		evaluator = spline.Geometry.Evaluator
			
			Dim endparam As Integer
			endparam = 1
			
			points = Int(endparam/stepSize)
			Dim arr((points+1)*2), tparam(points+1) As Double
			
			counter = 0
			For start = 0 To points Step 1
				tparam(counter) = start/points
				counter = counter + 1
			Next
			
        	evaluator.GetPointAtParam(tparam, arr)
        	For count = 0 To points Step 1
				coordinateData = coordinateData & arr(count*2) & ", " & arr(count*2+1) & vbCrLf	
			Next 
        ElseIf TypeOf entity Is SketchPoint
			Dim point As SketchPoint
			point = entity
			If point.AttachedEntities.Count
				Continue For
			End If
			coordinateData = coordinateData & "Point" & vbCrLf
			coords = point.Geometry
			coordinateData = coordinateData & coords.X & ", " & coords.Y & vbCrLf
		End If
    Next

    output = System.IO.File.CreateText(filePath)
    output.Write(coordinateData)
    output.Close()
End Sub