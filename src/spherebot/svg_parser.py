import inkex
from inkex.transforms import Transform
from inkex.bezier import cspsubdiv
from . import entities
from math import radians
import sys, pprint


class SvgIgnoredEntity:
  def load(self,node,mat):
    self.tag = node.tag
  def __str__(self):
    return "Ignored '%s' tag" % self.tag
  def get_gcode(self,context):
    return

class SvgPath(entities.PolyLine):
  def load(self, node, mat):
    transformed_path = node.path.to_absolute().transform(mat)
    p = transformed_path.to_superpath()
    cspsubdiv(p, flat=0.2)
    self.segments = [[tuple(csp[1]) for csp in sp] for sp in p if sp]

  def new_path_from_node(self, node):
    newpath = inkex.etree.Element(inkex.addNS('path','svg'))
    s = node.get('style')
    if s:
      newpath.set('style',s)
    t = node.get('transform')
    if t:
      newpath.set('transform',t)
    return newpath

class SvgRect(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    x = float(node.get('x'))
    y = float(node.get('y'))
    w = float(node.get('width'))
    h = float(node.get('height'))
    a = []
    a.append(['M ', [x,y]])
    a.append([' l ', [w,0]])
    a.append([' l ', [0,h]])
    a.append([' l ', [-w,0]])
    a.append([' Z', []])
    newpath.set('d', simplepath.formatPath(a))
    SvgPath.load(self,newpath,mat)

class SvgLine(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    x1 = float(node.get('x1'))
    y1 = float(node.get('y1'))
    x2 = float(node.get('x2'))
    y2 = float(node.get('y2'))
    a = []
    a.append(['M ', [x1,y1]])
    a.append([' L ', [x2,y2]])
    newpath.set('d', simplepath.formatPath(a))
    SvgPath.load(self,newpath,mat)

class SvgPolyLine(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    pl = node.get('points','').strip()
    if pl == '':
      return
    pa = pl.split()
    if not len(pa):
      return

    d = "M " + pa[0]
    for i in range(1, len(pa)):
      d += " L " + pa[i]
    newpath.set('d',d)
    SvgPath.load(self,newpath,mat)

class SvgEllipse(SvgPath):
  def load(self, node,mat):
    rx = float(node.get('rx','0'))
    ry = float(node.get('ry','0'))
    SvgPath.load(self,self.make_ellipse_path(rx,ry,node), mat)
  def make_ellipse_path(rx, ry, node):
    if rx == 0 or ry == 0:
      return None
    cx = float(node.get('cx','0'))
    cy = float(node.get('cy','0'))
    x1 = cx - rx
    x2 = cx + rx
    d = 'M %f,%f ' % (x1,cy) + \
      'A %f,%f ' % (rx,ry) + \
      '0 1 0 %f, %f ' % (x2,cy) + \
      'A %f,%f ' % (rx,ry) + \
      '0 1 0 %f,%f' % (x1,cy)
    newpath = self.new_path_from_node(node)
    newpath.set('d',d)
    return newpath
  
class SvgCircle(SvgEllipse):
  def load(self, node,mat):
    rx = float(node.get('r','0'))
    SvgPath.load(self,self.make_ellipse_path(rx,rx,node), mat)

class SvgText(SvgIgnoredEntity):
  def load(self,node,mat):
    inkex.errormsg('Warning: unable to draw text. please convert it to a path first.')
    SvgIgnoredEntity.load(self,node,mat)

class SvgLayerChange():
  def __init__(self,layer_name):
    self.layer_name = layer_name
  def get_gcode(self,context):
    context.codes.append("M01 (Plotting layer '%s')" % self.layer_name)

class SvgParser:

  entity_map = {
    'path': SvgPath,
    'rect': SvgRect,
    'line': SvgLine,
    'polyline': SvgPolyLine,
    'polygon': SvgPolyLine,
    'circle': SvgCircle,
    'ellipse': SvgEllipse,
    'pattern': SvgIgnoredEntity,
    'metadata': SvgIgnoredEntity,
    'defs': SvgIgnoredEntity,
    'eggbot': SvgIgnoredEntity,
    ('namedview','sodipodi'): SvgIgnoredEntity,
    'text': SvgText
  }

  def __init__(self, svg, pause_on_layer_change=False):
    self.svg = svg
    self.pause_on_layer_change = pause_on_layer_change
    self.entities = []

  def parse(self):
    self.svgWidth = self.svg.viewport_width
    self.svgHeight = self.svg.viewport_height
    initial_transform = Transform().add_scale(1,-1).add_translate(-(self.svgWidth / 2.0), -(self.svgHeight / 2.0))
    self.recursivelyTraverseSvg(self.svg, initial_transform)

  def recursivelyTraverseSvg(self, nodeList, 
                             matCurrent,
                             parent_visibility = 'visible'):
    """
    Recursively traverse the svg file to plot out all of the
    paths.  The function keeps track of the composite transformation
    that should be applied to each path.

    This function handles path, group, line, rect, polyline, polygon,
    circle, ellipse and use (clone) elements. Notable elements not
    handled include text.  Unhandled elements should be converted to
    paths in Inkscape.

    TODO: There's a lot of inlined code in the eggbot version of this
    that would benefit from the Entities method of dealing with things.
    """
    for node in nodeList:
      # Ignore invisible nodes
      v = node.get('visibility', parent_visibility)
      if v == 'inherit':
        v = parent_visibility
      if v == 'hidden' or v == 'collapse':
        pass

      matNew = matCurrent @ node.transform

      if node.tag == inkex.addNS('g','svg') or node.tag == 'g':
        if (node.get(inkex.addNS('groupmode','inkscape')) == 'layer'):
          layer_name = node.get(inkex.addNS('label','inkscape'))
          if self.pause_on_layer_change:
            self.entities.append(SvgLayerChange(layer_name))
        self.recursivelyTraverseSvg(node, matNew, parent_visibility = v)
      elif node.tag == inkex.addNS('use','svg') or node.tag == 'use':
        refid = node.get(inkex.addNS('href','xlink'))
        if refid:
          # [1:] to ignore leading '#' in reference
          path = '//*[@id="%s"]' % refid[1:]
          refnode = node.xpath( path )
          if refnode:
            x = float(node.get('x','0'))
            y = float(node.get('y','0'))
            if (x!=0) or (y!=0):
              matNew2 = matNew @ Transform(translate=(x, y))
            else:
              matNew2 = matNew
            v = node.get('visibility',v)
            self.recursivelyTraverseSvg(refnode,matNew2,parent_visibility=v)
          else:
            pass
        else:
          pass
      elif not isinstance(node.tag, str):
        pass
      else:
        entity = self.make_entity(node, matNew)
        if entity == None:
          inkex.errormsg('Warning: unable to draw object, please convert it to a path first.')

  def make_entity(self,node,mat):
    for nodetype in list(SvgParser.entity_map.keys()):
      tag = nodetype
      ns = 'svg'
      if(type(tag) is tuple):
        tag = nodetype[0]
        ns = nodetype[1]
      if node.tag == inkex.addNS(tag,ns) or node.tag == tag:
        constructor = SvgParser.entity_map[nodetype]
        entity = constructor()
        entity.load(node,mat)
        self.entities.append(entity)
        return entity
    return None
