#!/usr/bin/env python2
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # draw ground plane
        self.ground = self.createPlane((1,1))
        groundNodePath = self.render.attachNewNode(self.ground)
        size = 1000
        groundNodePath.setPos(-size/2, -size/2, 0);
        groundNodePath.setScale(size,size,size)

        # some fog
        fog = Fog("Fog Name")
        fog.setColor(1,1,1);
        fog.setExpDensity(0.005)
        fog.setMode(Fog.MExponentialSquared)
        self.render.attachNewNode(fog)
        self.render.setFog(fog)
        base.setBackgroundColor(1,1,1);

        # set up lights
        self.createLights()

        # a cube
        self.cube = self.loader.loadModel("models/box")
        self.cube.reparentTo(self.render)

        self.loadActor()

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    def createPlane(self, size):
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices", format, Geom.UHStatic)
        vdata.setNumRows(4)

        # define vertices
        vertexWriter = GeomVertexWriter(vdata, "vertex")
        vertexWriter.addData3f(0,0,0)
        vertexWriter.addData3f(size[0],0,0)
        vertexWriter.addData3f(size[0],size[1],0)
        vertexWriter.addData3f(0,size[1],0)

        # define two triangles via indices
        tris = GeomTriangles(Geom.UHStatic)
        tris.addVertex(0)
        tris.addVertex(1)
        tris.addVertex(3)
        tris.closePrimitive()
        tris.addConsecutiveVertices(1,3) #add vertex 1, 2 and 3
        tris.closePrimitive()

        # make a Geom object to hold the primitives
        squareGeom = Geom(vdata)
        squareGeom.addPrimitive(tris)
        squareGN = GeomNode("square")
        squareGN.addGeom(squareGeom)

        return squareGN

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 24.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

    def loadActor(self):
        # Load and transform the panda actor.
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)
        # Loop its animation.
        self.pandaActor.loop("walk")

        # Create the four lerp intervals needed for the panda to
        # walk back and forth.
        pandaPosInterval1 = self.pandaActor.posInterval(13,
                                                        Point3(0, -10, 0),
                                                        startPos=Point3(0, 10, 0))
        pandaPosInterval2 = self.pandaActor.posInterval(13,
                                                        Point3(0, 10, 0),
                                                        startPos=Point3(0, -10, 0))
        pandaHprInterval1 = self.pandaActor.hprInterval(3,
                                                        Point3(180, 0, 0),
                                                        startHpr=Point3(0, 0, 0))
        pandaHprInterval2 = self.pandaActor.hprInterval(3,
                                                        Point3(0, 0, 0),
                                                        startHpr=Point3(180, 0, 0))

        # Create and play the sequence that coordinates the intervals.
        self.pandaPace = Sequence(pandaPosInterval1,
                                  pandaHprInterval1,
                                  pandaPosInterval2,
                                  pandaHprInterval2,
                                  name="pandaPace")
        self.pandaPace.loop()


    def createLights(self):
        # lights
        self.light = DirectionalLight('directionalLight')
        self.light.setColor(Vec4(0.8, 0.8, 0.5, 1))
        self.light.getLens().set_near_far(-10.0, 50.0)
        self.light.getLens().setFilmSize(41, 21)
        self.lightNP = self.render.attachNewNode(self.light)
        self.lightNP.setHpr(180, -20, 0)
        self.light.setShadowCaster(True, 1024, 1024)
        self.render.setLight(self.lightNP)

        self.ambientLight = AmbientLight('ambientLight')
        self.ambientLight.setColor(Vec4(0.4, 0.4, 0.5, 1))
        self.ambientLightNP = self.render.attachNewNode(self.ambientLight)
        self.render.setLight(self.ambientLightNP)

        self.render.setShaderAuto()


app = MyApp()
app.run()
