Modifications To Original by Firebovine
=======================================

I have modified this slightly. This branch is "pixel perfect", so it is meant to be used to generate 1:1 pixels:steps with your machine.
It is meant to be used with my own SphereBot firmware branch, available at https://github.com/firebovine/SphereBot
It generates the correct g-code for use with that firmware to pause on pen changes (along with the Utils/feeder.py).
It also adds a neat option which adds deceleration to the pen movements after a certain position. This allows you to "softly" contact the egg,
which I found yields better results, especially when doing tons of stippling type moves.

2026 Update - Now works with modern Inkscape versions! Woohoo!


SphereBot G-Code Output for Inkscape
===========================================

This is an Inkscape extension that allows you to save your Inkscape drawings as
G-Code files suitable for plotting with the SphereBot: http://www.thingiverse.com/thing:7656
I used one of the 3d printed variants with minor modifications, but the electronics I used are from the above thingiverse link.

Original Author: [Marty McGuire](http://github.com/martymcguire)
Original Author's Website: [http://github.com/martymcguire/inkscape-unicorn](http://github.com/martymcguire/inkscape-unicorn)

Credits
=======

* Firebovine made some modifications to work with SphereBot, with firebovine's 1:1 firmware
* Marty McGuire pulled this all together into an Inkscape extension.
* [Inkscape](http://www.inkscape.org/) is an awesome open source vector graphics app.
* [Scribbles](https://github.com/makerbot/Makerbot/tree/master/Unicorn/Scribbles%20Scripts) is the original DXF-to-Unicorn Python script.
* [The Egg-Bot Driver for Inkscape](http://code.google.com/p/eggbotcode/) provided inspiration and good examples for working with Inkscape's extensions API.

Install
=======

Copy the contents of `src/` to your Inkscape `extensions/` folder.

Typical locations include:

* OS X - `/Applications/Inkscape.app/Contents/Resources/extensions`
* Linux - `/usr/share/inkscape/extensions`
* Windows - `C:\Program Files\Inkscape\share\extensions`

Usage
=====

* Size and locate your image appropriately:
	* This is dependent on your hardware. Use PIXELS, and set your image size to be the same as your hardware steps. See Firebovine's SphereBot firmware README for more.
* Convert all text to paths:
	* Select all text objects.
	* Choose **Path | Object to Path**.
* Save as G-Code:
	* **File | Save a Copy**.
	* Select **SphereBot G-Code (\*.gcode)**.
	* Save your file.
* Preview
	* For OS X, [Pleasant3D](http://www.pleasantsoftware.com/developer/pleasant3d/index.shtml) is great for this.
	* For other operating systems... I don't know!
  * Random gcode viewers sorta work.
* Print!
  * Use firebovine's SphereBot/Utils/feeder.py to send the gcode to the SphereBot.

TODOs
=====
* Many code paths are dead and can be simplified!
