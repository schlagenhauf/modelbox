#!/usr/bin/env python2
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *
from math import sqrt

from google import protobuf
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

        # create axis arrows
        self.axes = self.createAxisArrows()
        axesNodePath = self.render.attachNewNode(self.axes)
        axesNodePath.setRenderModeThickness(3)

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
        """
        q = LQuaternion()
        self.cube1 = self.loader.loadModel("models/camera")
        self.cube1.setColorScale(2.2,2.2,2.2,1)
        self.cube1.reparentTo(self.render)
        self.cube1.setPos(3,0,2)
        q.set(1,0,0,0)
        print q.getHpr()
        self.cube1.setQuat(q)

        self.cube2 = self.loader.loadModel("models/camera")
        self.cube2.setColorScale(2.2,2.2,2.2,1)
        self.cube2.reparentTo(self.render)
        self.cube2.setPos(1,0,2)
        q.set(0,1,0,0)
        self.cube2.setQuat(q)

        self.cube3 = self.loader.loadModel("models/camera")
        self.cube3.setColorScale(2.2,2.2,2.2,1)
        self.cube3.reparentTo(self.render)
        self.cube3.setPos(-1,0,2)
        q.set(0,0,1,0)
        self.cube3.setQuat(q)

        self.cube4 = self.loader.loadModel("models/camera")
        self.cube4.setColorScale(2.2,2.2,2.2,1)
        self.cube4.reparentTo(self.render)
        self.cube4.setPos(-3,0,2)
        q.set(0,0,0,1)
        self.cube4.setQuat(q)
        """

        self.cube_meas = self.loader.loadModel("models/camera")
        self.cube_meas.setColorScale(1.2,1.2,1.2,1)
        self.cube_meas.reparentTo(self.render)
        self.cube_meas.setPos(2,0,2)
        self.cube_ref = self.loader.loadModel("models/camera")
        self.cube_ref.setColorScale(2,0.8,0.8,0.5)
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


    def fetchMessages(self, task):
        try:
            data = self.receiver.recv(flags=zmq.NOBLOCK)
            msg = RenderMessage()
            msg.ParseFromString(data)
            qRef = LQuaternion()
            qRef.set(msg.reference.w, msg.reference.x, msg.reference.y, msg.reference.z)
            qTrans = LQuaternion()
            qTrans.set(0, 1/sqrt(2), 1/sqrt(2), 0)
            qRefPrime = - qTrans * qRef * qTrans
            qAct = LQuaternion()
            qAct.set(msg.actual.w, msg.actual.x, msg.actual.y, msg.actual.z)
            qActPrime = - qTrans * qAct * qTrans

            self.cube_ref.setQuat(qRefPrime)
            self.cube_meas.setQuat(qActPrime)
            print "w: %f, x: %f, y: %f, z: %f" % (msg.reference.w, msg.reference.x, msg.reference.y, msg.reference.z)
            print "hpr: %s" % qRef.getHpr()
        except zmq.error.Again:
            pass
        except protobuf.message.DecodeError as e:
            logging.error(str(e))


        return Task.cont

    def createAxisArrows(self):
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices", format, Geom.UHStatic)
        vdata.setNumRows(4)

        # define vertices
        vertexWriter = GeomVertexWriter(vdata, "vertex")
        vertexWriter.addData3f(0,0,0)
        vertexWriter.addData3f(1,0,0)
        vertexWriter.addData3f(0,1,0)
        vertexWriter.addData3f(0,0,1)

        # define two triangles via indices
        lines = GeomLines(Geom.UHStatic)
        lines.addVertex(0)
        lines.addVertex(1)
        lines.addVertex(0)
        lines.addVertex(2)
        lines.addVertex(0)
        lines.addVertex(3)
        lines.closePrimitive()

        # make a Geom object to hold the primitives
        axisArrows = Geom(vdata)
        axisArrows.addPrimitive(lines)
        axisArrowNode = GeomNode("AxisArrows")
        axisArrowNode.addGeom(axisArrows)

        # attach labels
        xLabel = TextNode('xLabel')
        xLabel.setText('X')

        return axisArrowNode


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
