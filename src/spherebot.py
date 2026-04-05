#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spherebot G-code Exporter
Compatible with Python 3.14 and Inkscape 1.2+
"""
import inkex
import os

from spherebot.context import GCodeContext
from spherebot.svg_parser import SvgParser

class SpherebotOutput(inkex.OutputExtension):

    def add_arguments(self, pars):
        pars.add_argument("--pen_up_angle", type=float, default=5.0, help="Pen Up Angle")
        pars.add_argument("--pen_down_angle", type=float, default=50.0, help="Pen Down Angle")
        pars.add_argument("--start_delay", type=float, default=150.0, help="Delay after pen down command before movement in milliseconds")
        pars.add_argument("--stop_delay", type=float, default=150.0, help="Delay after pen up command before movement in milliseconds")
        pars.add_argument("--xy_feedrate", type=float, default=8500.0, help="XY axes feedrate in mm/min")
        pars.add_argument("--z_feedrate", type=float, default=150.0, help="Z axis feedrate in mm/min")
        pars.add_argument("--z_height", type=float, default=0.0, help="Z axis print height in mm")
        pars.add_argument("--finished_height", type=float, default=0.0, help="Z axis height after printing in mm")
        pars.add_argument("--register_pen", type=inkex.Boolean, default=True, help="Add pen registration check(s)")
        pars.add_argument("--x_home", type=float, default=0.0, help="Starting X position")
        pars.add_argument("--y_home", type=float, default=0.0, help="Starting Y position")
        pars.add_argument("--pause_on_layer_change", type=inkex.Boolean, default=True, help="Pause on layer changes.")
        pars.add_argument("--tab", type=str, help="Inkscape tab identifier")

    def save(self, stream):
        inkex.utils.debug("Starting Spherebot export...")
      

        doc_path = self.document_path()
        filename = os.path.basename(doc_path) if doc_path else "unsaved.svg"

        context = GCodeContext(self.options.xy_feedrate, self.options.z_feedrate, 
                           self.options.start_delay, self.options.stop_delay,
                           self.options.pen_up_angle, self.options.pen_down_angle,
                           self.options.z_height, self.options.finished_height,
                           self.options.x_home, self.options.y_home,
                           self.options.register_pen,
                           filename)


        self.preprocess()
        root = self.document.getroot()
        parser = SvgParser(root, self.options.pause_on_layer_change)
        parser.parse()

        for entity in parser.entities:
            entity.get_gcode(context)

        gcode = context.generate()

        stream.write(gcode.encode("utf-8"))

        inkex.utils.debug("Finished SphereBot export.")

if __name__ == "__main__":
    SpherebotOutput().run()
