#!/usr/bin/env python2
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *

from rendermsg_pb2 import *
import zmq
import logging

class Modelbox(ShowBase):
    def __init__(self, ipAddr = 'localhost', port = '6666'):
        ShowBase.__init__(self)

        # draw ground plane
        self.ground = self.createPlane((1,1))
        groundNodePath = self.render.attachNewNode(self.ground)
        size = 1000
        groundNodePath.setPos(-size/2, -size/2, 0);
        groundNodePath.setScale(size,size,size)

        # some fog
        fog = Fog("FogName")
        fog.setColor(1,1,1);
        fog.setExpDensity(0.005)
        fog.setMode(Fog.MExponentialSquared)
        self.render.attachNewNode(fog)
        self.render.setFog(fog)
        base.setBackgroundColor(1,1,1);

        # set up lights
        self.createLights()

        # two objects
        self.cube_meas = self.loader.loadModel("models/camera")
        self.cube_meas.reparentTo(self.render)
        self.cube_meas.setPos(2,0,2)
        self.cube_ref = self.loader.loadModel("models/camera")
        self.cube_ref.reparentTo(self.render)
        self.cube_ref.setPos(-2,0,2)

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # set up networking
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PAIR)
        self.receiver.bind('tcp://*:%s' % port)
        logging.info('Listening on port %s' % port)
        self.taskMgr.add(self.fetchMessages, "FetchMessages")

        ## test sender
        #self.sender = self.context.socket(zmq.PAIR)
        #self.sender.connect('tcp://%s:%s' % (ipAddr, port))
        #logging.info('Client connected to %s:%s' % (ipAddr, port))


    def fetchMessages(self, task):
        #inQuat = LQuaternion()
        #inQuat.setHpr(LVector3f(sin(task.time),1,0), CS_default)
        #rm = RenderMessage()
        #rm.reference.w = inQuat.getW()
        #rm.reference.x = inQuat.getX()
        #rm.reference.y = inQuat.getY()
        #rm.reference.z = inQuat.getZ()
        #rm.actual.w = 1
        #rm.actual.x = 0
        #rm.actual.y = 0
        #rm.actual.z = 0
        #self.sender.send(rm.SerializeToString())

        try:
            data = self.receiver.recv(flags=zmq.NOBLOCK)
            msg = RenderMessage()
            msg.ParseFromString(data)
            qRef = LQuaternion()
            qRef.set(msg.reference.x, msg.reference.y, msg.reference.z, msg.reference.w)
            qAct = LQuaternion()
            qAct.set(msg.actual.x, msg.actual.y, msg.actual.z, msg.actual.w)
            self.cube_ref.setQuat(qRef)
            self.cube_meas.setQuat(qAct)
        except zmq.error.Again:
            pass

        return Task.cont


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
        angleDegrees = 35
        #angleDegrees = task.time * 24.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 10)
        self.camera.setHpr(angleDegrees, -20, 0)
        return Task.cont

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


if __name__=='__main__':
    app = Modelbox()
    app.run()
