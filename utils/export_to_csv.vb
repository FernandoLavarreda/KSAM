'Fernando Lavarreda
'Export Inventor sketch to csv, by diffult pick the first sketch
Sub Main()
    Dim partDoc As PartDocument
    partDoc = ThisApplication.ActiveDocument

    ' Assuming the sketch you want to export is the first sketch in the document
    Dim sketch As Sketch
    sketch_num = 1
    sketch = partDoc.ComponentDefinition.Sketches.Item(sketch_num)

    filePath = "C:\Users\ferna\Downloads\out.txt"

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
        
		End If
    Next

    output = System.IO.File.CreateText(filePath)
    output.Write(coordinateData)
    output.Close()
End Sub