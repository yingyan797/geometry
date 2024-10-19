# Geometrical & Physical animation program + Pixel drawing

## Introduction
The application has 2 main parts: 
1) Animation generation according to geometry & physics (web UI integration working in progress)
2) Pixel drawing with canvas database (web UI available)

## System setup
1. Python Flask, numpy, matplotlib, and PIL are required
2. [Pixel drawing] Clone code, run app.py, and open browser at localhost:5002 to view both applications
3. [Geometric animation] Edit the main function of trajectory.py to generate GIF animations 
4. [Physics simulation] Edit the main function of universe.py to create trajectory of point masses

See "static" folder for some example animation created using Python PIL
Project under development, will include Python Flask web interface for animation in the future.

## Usage instructions
(Pixel drawing only)
1. Create canvas with number of rows, columns specified (default 20 by 30)
2. Click on any of the color options
3. Click on the canvas positions to apply color on one pixel
4. To fill color in a rectangular region, click on 2 points of the left bar (for row range) and 2 points of the top bars (column range). Then press "Fill color in the region"
5. Enter a name for the drawing and save to database (either updating existing one or create copy)
6. To load a drawing from database, choose from the drop down menu (e.g., #1 sample drawing (20x30)) and click "Load"
7. Click "Delete" to remove the drawing corresponding to the [Session number] e.g. #3
8. Render the drawing as a PNG image to see how it looks like (png file save as static/canvas.png)

New feature: pixel drawing. Dowload code, launch app.py on localhost:5002 to view the application, where user can draw logos, flags, characters, etc., with mouse click.
