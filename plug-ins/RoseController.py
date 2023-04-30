# -*- coding: utf-8 -*
import sys
import math
import random
import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
import Vector3 as v3
import BackCalcBushRose as br

def maya_useNewAPI(): #for api2.0
    pass

# ウィンドウ用

#　枝のパラメータをまとめた基底クラス
#　枝の長さの目安 sl * sn
class BranchParameter :
    def __init__(self,thickness = 1.,sl = 3,sn = 7,smooth = 1) :
        #　枝の太さ cm
        self.thickness = thickness
        #　節の長さ cm
        self.sectionLength = sl
        #　最大の節の数
        self.sectionNum = sn
        #　滑らかさ
        self.smoothness = smooth
    
    def setWindow(self) :
        '''　ウィンドウにセットする　'''
        with pm.horizontalLayout() :
            pm.text('SectionLength')
            self.sectionLength = pm.floatField(value = self.sectionLength)
        with pm.horizontalLayout() :
            pm.text('Thickness')
            self.thickness = pm.floatField(min = 0,max = 5,value = self.thickness)
        with pm.horizontalLayout() :
            pm.text('Smoothness')
            self.smoothness = pm.intField(value = self.smoothness)

# シュートのパラメータクラス
class ShootParameter(BranchParameter) :
    def __init__(self,thickness = 0.75,sl = 7,smooth = 1,ph = 40,pw = 40,sn = 4) :
        super().__init__(thickness,sl,0,smooth)
        #　シュートをピンチする高さ
        self.pinchHeight = ph
        #　シュートをピンチする楕円の傾き　　y / xz
        self.pinchWidth = pw
        #　シュートの数
        self.shootNum = sn

        self.directions = [0] * sn * 3
    
    def setWindow(self) :
        with pm.horizontalLayout() :
            pm.text('ShootNum')
            self.shootNum = pm.intField(value = self.shootNum)
        with pm.horizontalLayout() :
            pm.text('PinchHeight')
            self.pinchHeight = pm.floatField(value = self.pinchHeight)
        with pm.horizontalLayout() :
            pm.text('PinchWidth')
            self.pinchWidth = pm.floatField(value = self.pinchWidth)
        super().setWindow()
        
        

# 前年までに生えてきた枝
class OldBranchParameter(BranchParameter) :
    def __init__(self,thickness = 0.5,sl = 5,sn = 6,smooth = 1,ph = 70,pw = 70) :
        super().__init__(thickness,sl,sn,smooth)
        #　剪定する高さ y
        self.pruneHeight = ph
        #　剪定する幅　　xz
        self.pruneWidth = pw

    def setWindow(self) :
        with pm.horizontalLayout() :
            pm.text('PruneHeight')
            self.pruneHeight = pm.floatField(value = self.pruneHeight)
        with pm.horizontalLayout() :
            pm.text('PruneWidth')
            self.pruneWidth = pm.floatField(value = self.pruneWidth)
        with pm.horizontalLayout() :
            pm.text('SectionNum')
            self.sectionNum = pm.intField(value = self.sectionNum)
        super().setWindow()

# 花が咲く枝 (その年に生えた枝)
class FlowerBranchParameter(BranchParameter) :
    def __init__(self,thickness = 0.3,sl = 5,sn = 7,smooth = 1,fnum = 1,g = math.pi/2) :
        super().__init__(thickness,sl,sn,smooth)
        #　花数
        self.flowerNum = fnum
        #　枝全体が垂れ下がる大きさ　 0~1
        #　下がらない時　 0
        self.gravity = g

    def setWindow(self) :
        with pm.horizontalLayout() :
            pm.text('FlowerNum')
            self.flowerNum = pm.intField(min = 1,max = 10,value = self.flowerNum)
        with pm.horizontalLayout() :
            pm.text('Gravity')
            self.gravity = pm.floatSlider(min = -math.pi/2,max = math.pi/2, step = 0.01, value = self.gravity)
        with pm.horizontalLayout() :
            pm.text('SectionNum')
            self.sectionNum = pm.intField(value = self.sectionNum)
        super().setWindow()
        

# バラ全体のパラメータ
# 葉と花についてのパラメータはそのうち用意する。
# ウィンドウ込み
class RoseParameter:
    def __init__(self,smoothness = 16,inclination = math.pi / 3, strength = 10,flowerStrength = 3,flowerExponent = 1.2,exponent = 1,lh = 0.1,prob = 5,FlowerBranchProbability = 20,b = OldBranchParameter(),sb = ShootParameter(),fb = FlowerBranchParameter()) :
        
        # window
        if pm.window("RoseWindow", exists = True):
            return
        self.window = pm.window("RoseWindow", t = "BushRose", w = 546, h = 100)
        pm.columnLayout(adj = True)
        with pm.horizontalLayout() :
            pm.text('Name')
            self.Name = pm.textField('objctName',text = 'BushRose')
        with pm.horizontalLayout() :
            pm.text('LeafObjctName')
            self.LeafName = pm.textField('leafObjctName',text = 'leaf_GEO')
        with pm.horizontalLayout() :
            pm.text('FlowerObjctName')
            self.FlowerName = pm.textField('flowerObjctName',text = 'flower_GEO')

        # 枝の円の分割
        self.Smoothness = pm.intSliderGrp(label='Smoothness', field=True, min=3, max=64, value=smoothness)
        # 枝の傾き
        self.Inclination = pm.floatSliderGrp(label='BranchInclination', field=True, min=0, max=math.pi / 2, step = 0.01, value=inclination)
        # 枝の曲がる強さ
        self.Strength =  pm.intSliderGrp(label='Strength', field=True, min=1, max=32, value=strength)
        # 枝の重みの指数部
        self.WeightExponent = pm.floatSliderGrp(label='WeightExponent', field=True, min=0, max = 2, step = 0.01, value=exponent)
        # 花枝の曲がる強さ
        self.FlowerStrength =  pm.intSliderGrp(label='FlowerStrength', field=True, min=1, max=32, value=flowerStrength)
        # 花枝の重みの指数部
        self.FlowerWeightExponent = pm.floatSliderGrp(label='FlowerWeightExponent', field=True, min=0, max = 2, step = 0.01, value=flowerExponent)
        # 枝の生えやすさ (%)
        self.Probability = pm.intSliderGrp(label='Probability', field=True, min=0, max=100, value=prob)
        # 花枝の生えやすさ (%)
        self.FlowerBranchProbability = pm.intSliderGrp(label='FlowerBranchProbability', field=True, min=0, max=100, value=FlowerBranchProbability)
        # 新梢が生えてくる　一番低い所のたかさ　0~1
        self.LowestHeight = pm.floatSliderGrp(label='LowestHeight', field=True, min=0, max=1, step = 0.01, value=lh)
        # 近接の距離
        self.KillDiff = pm.floatSliderGrp(label='KillDiff', field=True, min=0, max=20, step = 0.01, value=2)

        # 株の高さ
        with pm.horizontalLayout() :
            pm.text('Height')
            self.Height = pm.intField(min = 10,max = 300,value = 100)

        # 株の高さ
        with pm.horizontalLayout() :
            pm.text('Width')
            self.Width = pm.intField(min = 10,max = 300,value = 100)


        # 枝のパラメータ
        self.BranchParam = b
        self.ShootParam = sb
        self.FlowerBParam = fb

        with pm.tabLayout() as tabs :
            with pm.columnLayout(adj = True) as shootTab:
                self.ShootParam.setWindow()
            with pm.columnLayout(adj = True) as branchTab:
                self.BranchParam.setWindow()
            with pm.columnLayout(adj = True) as flowerBT:
                self.FlowerBParam.setWindow()
        tabs.setTabLabel([shootTab,u'Shoot'])
        tabs.setTabLabel([branchTab,u'Branch'])
        tabs.setTabLabel([flowerBT,u'flowerBranch'])

        pm.button(label = 'Curve', command = self.CreateCurve)
        pm.button(label = 'Mesh', command = self.CreateMesh)
        pm.button(label = 'Leaf', command = self.SetLeaves)
        pm.button(label = 'Flower', command = self.SetFlowers)

        pm.showWindow(self.window)
    
    # ちょうどいい高さを２部探索で探す
    def heightBinarySearch(self, upperLimit, lowerLimit) :
        h = (upperLimit + lowerLimit) / 2
        print(type(h),"binary search")
        if upperLimit - lowerLimit <= 5 :
            self.pruneHeight = h
            self.pinchHeight = max(10,h/2)
        else :
            self.brt = self.Tree(h,self.Width.getValue(),max(10,h/2),max(10,self.Width.getValue()))
            print('h' + str(h) + ', ' + str(self.brt.Top()))
            if self.Height.getValue() > self.brt.Top() :
                self.heightBinarySearch(upperLimit,h)
            else :
                self.heightBinarySearch(h,lowerLimit)

    def widthBinarySearch(self, upperLimit, lowerLimit) :
        w = (upperLimit + lowerLimit) / 2
        if upperLimit - lowerLimit <= 5 :
            self.pruneWidth = w
            self.pinchWidth = max(10,w/2)
        else :
            print('w' + str(w) + ', ' + str(self.pruneWidth))
            self.brt = self.Tree(self.pruneHeight,w,self.pinchHeight,max(10,w/2))
            if self.brt.isLarge(self.Height.getValue(),self.Width.getValue()) :
                self.widthBinarySearch(w,lowerLimit)
            else :
                self.widthBinarySearch(upperLimit,w)

    # curveを作る
    # 引数の *args コマンドとして扱う用
    def CreateCurve(self,*args) :
        self.pruneHeight = self.BranchParam.pruneHeight.getValue()
        self.pruneWidth = self.BranchParam.pruneWidth.getValue()
        self.pinchHeight = self.ShootParam.pinchHeight.getValue()
        self.pinchWidth = self.ShootParam.pinchWidth.getValue()
        if mc.getAttr('CrownEllipsoid.visibility'):
            self.heightBinarySearch(self.Height.getValue(), 10)
            self.widthBinarySearch(self.Width.getValue(), 10)
            self.BranchParam.pruneHeight.setValue(self.pruneHeight)
            self.BranchParam.pruneWidth.setValue(self.pruneWidth)
            self.ShootParam.pinchHeight.setValue(self.pinchHeight)
            self.ShootParam.pinchWidth.setValue(self.pinchWidth)
            mc.setAttr('ShootEllipsoid.sx', self.pinchWidth)
            mc.setAttr('ShootEllipsoid.sy', self.pinchHeight)
            mc.setAttr('BranchEllipsoid.sx', self.pruneWidth)
            mc.setAttr('BranchEllipsoid.sy', self.pruneHeight)
        self.brt = self.Tree(self.pruneHeight,self.pruneWidth,self.pinchHeight,self.pinchWidth)
        self.brt.CreateCurve()
    
    def Tree(self, pruneHeight,pruneWidth,pinchHeight,pinchWidth) :
        print(pruneHeight)
        return br.BushRoseTree \
            (pm.textField(
                self.Name, q=True, text=True),
                self.Smoothness.getValue(),
                self.Inclination.getValue(),
                self.Strength.getValue(),
                self.WeightExponent.getValue(),
                self.Probability.getValue(),
                self.FlowerBranchProbability.getValue(),
                self.LowestHeight.getValue(),
                self.KillDiff.getValue(),
                pinchHeight,
                pinchWidth,
                self.ShootParam.sectionLength.getValue(),
                self.ShootParam.thickness.getValue(),
                self.ShootParam.smoothness.getValue(),
                self.ShootParam.shootNum.getValue(),
                self.ShootParam.directions,
                pruneHeight,
                pruneWidth,
                self.BranchParam.sectionNum.getValue(),
                self.BranchParam.sectionLength.getValue(),
                self.BranchParam.thickness.getValue(),
                self.BranchParam.smoothness.getValue(),
                self.FlowerBParam.flowerNum.getValue(),
                self.FlowerBParam.gravity.getValue(),
                self.FlowerBParam.sectionNum.getValue(),
                self.FlowerBParam.sectionLength.getValue(),
                self.FlowerBParam.thickness.getValue(),
                self.FlowerBParam.smoothness.getValue(),
                self.FlowerStrength.getValue(),
                self.FlowerWeightExponent.getValue()
            )
    
    # メッシュをつける
    def CreateMesh(self,*args) :
        if self.brt == None :
            self.brt = br.BushRoseTree \
                ( \
                    pm.textField(self.Name, q=True, text=True), \
                    self.Smoothness.getValue(), self.Inclination.getValue(), self.Strength.getValue(), self.WeightExponent.getValue(), self.Probability.getValue(), self.LowestHeight.getValue(), \
                    self.ShootParam.pinchHeight.getValue(), self.ShootParam.pinchWidth.getValue(), self.ShootParam.sectionLength.getValue(), self.ShootParam.thickness.getValue(), self.ShootParam.smoothness.getValue(), self.ShootParam.shootNum.getValue(), \
                    self.BranchParam.pruneHeight.getValue(), self.BranchParam.pruneWidth.getValue(), self.BranchParam.sectionNum.getValue(), self.BranchParam.sectionLength.getValue(), self.BranchParam.thickness.getValue(), self.BranchParam.smoothness.getValue(), \
                    self.FlowerBParam.flowerNum.getValue(), self.FlowerBParam.gravity.getValue(), \
                    self.FlowerBParam.sectionNum.getValue(), self.FlowerBParam.sectionLength.getValue(), self.FlowerBParam.thickness.getValue(), self.FlowerBParam.smoothness.getValue(), \
                )
        self.brt.SetMesh()

    def SetLeaves(self,*args) :
        self.brt.SetLeaves(pm.textField(self.LeafName, q=True, text=True))

    def SetFlowers(self,*args) :
        self.brt.setFlowers(pm.textField(self.FlowerName, q=True, text=True))

roseParameter = None # global variable


class RoseBuild(om.MPxCommand):
    kCmdName = 'RoseBuild'

    def __init__(self):
        om.MPxCommand.__init__(self)

    def doIt(self, args):
        global roseParameter
        roseParameter = RoseParameter()

        mc.sphere(name = 'ShootEllipsoid')
        mc.sphere(name = 'BranchEllipsoid')
        mc.sphere(name = 'CrownEllipsoid')
        mc.setAttr('ShootEllipsoid.scale',  40, 40, 40)
        mc.setAttr('BranchEllipsoid.scale', 70, 70, 70)
        mc.setAttr('CrownEllipsoid.scale',  100, 100, 100)
        mc.connectAttr('ShootEllipsoid.sx',  'ShootEllipsoid.sz')
        mc.connectAttr('BranchEllipsoid.sx', 'BranchEllipsoid.sz')
        mc.connectAttr('CrownEllipsoid.sx',  'CrownEllipsoid.sz')
        mc.setAttr('ShootEllipsoid.visibility', 0)
        mc.setAttr('BranchEllipsoid.visibility', 0)
        mc.setAttr('CrownEllipsoid.visibility', 1)
        ctrl = mc.createNode('RoseController')
        mc.connectAttr('ShootEllipsoid.sx', ctrl + '.shootWidth')
        mc.connectAttr('ShootEllipsoid.sy', ctrl + '.shootHeight')
        mc.connectAttr('BranchEllipsoid.sx', ctrl + '.branchWidth')
        mc.connectAttr('BranchEllipsoid.sy', ctrl + '.branchHeight')
        mc.connectAttr('CrownEllipsoid.sx', ctrl + '.crownWidth')
        mc.connectAttr('CrownEllipsoid.sy', ctrl + '.crownHeight')
        mc.sphere(name = 'dummy')
        mc.connectAttr(ctrl + '.output', 'dummy.sx')
        mc.connectAttr(ctrl + '.output', 'dummy.sy')
        mc.connectAttr(ctrl + '.output', 'dummy.sz')

        numShoots = roseParameter.ShootParam.shootNum.getValue()
        if len(args) > 0:
            numShoots = args.asInt(0)
        dirs = [0.0] * numShoots * 3
        cyllen = 10
        for i in range(numShoots):
            sname = mc.polyCylinder(name = 'shoot' + str(i), height = cyllen, radius = 1)
            sname = sname[0]
            mc.move(0, cyllen / 2, 0)
            mc.xform(ws = True, rp = (0, 0, 0))
            mc.xform(ws = True, sp = (0, 0, 0))
            mc.connectAttr(sname + '.sx', sname + '.sz')
            if i > 0:
                mc.connectAttr('shoot0.sx', sname + '.sx')
                mc.connectAttr('shoot0.sy', sname + '.sy')
            rx = random.uniform(0, 90)
            ry = random.uniform(0, 360)
            mc.rotate(rx, ry, 0)
            v = om.MVector(0, 1, 0).rotateBy(
                    om.MEulerRotation(math.radians(rx), math.radians(ry), 0))
            dirs[i * 3 + 0] = v.x
            dirs[i * 3 + 1] = v.y
            dirs[i * 3 + 2] = v.z
            mc.connectAttr(sname + '.rx', ctrl + '.' + sname + '.' + sname + '0')
            mc.connectAttr(sname + '.ry', ctrl + '.' + sname + '.' + sname + '1')
            mc.connectAttr(sname + '.rz', ctrl + '.' + sname + '.' + sname + '2')
        mc.connectAttr('shoot0.sx', ctrl + '.probScale') #shoot0 -> probability scale
        mc.connectAttr('shoot0.sy', ctrl + '.inclRatio') #shoot0 -> strength scale

        roseParameter.ShootParam.shootNum.setValue(numShoots)
        roseParameter.ShootParam.directions = dirs

    @staticmethod
    def creator():
        return RoseBuild()


class RoseRegenerate(om.MPxCommand):
    kCmdName = 'RoseRegenerate'

    def __init__(self):
        om.MPxCommand.__init__(self)

    def doIt(self, args):
        global roseParameter
        if len(mc.ls('BushRose_GRP')) > 0:
            mc.delete('BushRose_GRP')
        roseParameter.CreateCurve()
    
    @staticmethod
    def creator():
        return RoseRegenerate()


class RoseController(om.MPxNode):
    kNodeName = 'RoseController'
    kNodeId = om.MTypeId(0x00001)

    shootHeight  = None
    shootWidth   = None
    shootDirs    = None
    branchHeight = None
    branchWidth  = None
    crownHeight  = None
    crownWidth   = None
    probScale    = None
    inclRatio    = None
    output       = None

    def __init__(self):
        self.probBranch = roseParameter.Probability.getValue()
        self.probFlower = roseParameter.FlowerBranchProbability.getValue()
        om.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        global roseParameter
        if plug != RoseController.output:
            return om.kUnknownParameter
        sh = dataBlock.inputValue(RoseController.shootHeight).asDouble()
        sw = dataBlock.inputValue(RoseController.shootWidth).asDouble()
        bh = dataBlock.inputValue(RoseController.branchHeight).asDouble()
        bw = dataBlock.inputValue(RoseController.branchWidth).asDouble()
        ch = dataBlock.inputValue(RoseController.crownHeight).asDouble()
        cw = dataBlock.inputValue(RoseController.crownWidth).asDouble()
        ps = dataBlock.inputValue(RoseController.probScale).asDouble()
        ir = dataBlock.inputValue(RoseController.inclRatio).asDouble()
        ir = 2.0 - max(0.01, min(ir, 2.0))
        roseParameter.ShootParam.pinchHeight.setValue(sh)
        roseParameter.ShootParam.pinchWidth.setValue(sw)
        roseParameter.BranchParam.pruneHeight.setValue(bh)
        roseParameter.BranchParam.pruneWidth.setValue(bw)
        roseParameter.Height.setValue(ch)
        roseParameter.Width.setValue(cw)
        roseParameter.Probability.setValue(self.probBranch * ps)
        roseParameter.FlowerBranchProbability.setValue(self.probFlower * ps)
        roseParameter.Inclination.setValue(ir)
        sn = roseParameter.ShootParam.shootNum.getValue()
        for i in range(sn):
            rv = dataBlock.inputValue(RoseController.shootDirs[i]).asDouble3()
            v = om.MVector(0, 1, 0).rotateBy(
                    om.MEulerRotation(
                        math.radians(rv[0]),
                        math.radians(rv[1]),
                        math.radians(rv[2])))
            roseParameter.ShootParam.directions[i * 3 + 0] = v[0]
            roseParameter.ShootParam.directions[i * 3 + 1] = v[1]
            roseParameter.ShootParam.directions[i * 3 + 2] = v[2]
        outputHandle = dataBlock.outputValue(RoseController.output)
        outputHandle.setDouble(0.0)
        dataBlock.setClean(plug)

    @staticmethod
    def creator():
        return RoseController()

    @staticmethod
    def initializer():
        nAttr = om.MFnNumericAttribute()
        RoseController.output = nAttr.create('output', 'o', om.MFnNumericData.kDouble, 0.0)
        nAttr.readable = True
        RoseController.addAttribute(RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.shootHeight = nAttr.create('shootHeight', 'sh', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.shootHeight)
        RoseController.attributeAffects(RoseController.shootHeight,  RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.shootWidth = nAttr.create('shootWidth', 'sw', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.shootWidth)
        RoseController.attributeAffects(RoseController.shootWidth,   RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.branchHeight = nAttr.create('branchHeight', 'bh', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.branchHeight)
        RoseController.attributeAffects(RoseController.branchHeight, RoseController.output)
        
        nAttr = om.MFnNumericAttribute()
        RoseController.branchWidth = nAttr.create('branchWidth', 'bw', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.branchWidth)
        RoseController.attributeAffects(RoseController.branchWidth,  RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.crownHeight = nAttr.create('crownHeight', 'ch', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.crownHeight)
        RoseController.attributeAffects(RoseController.crownHeight, RoseController.output)
        
        nAttr = om.MFnNumericAttribute()
        RoseController.crownWidth = nAttr.create('crownWidth', 'cw', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.crownWidth)
        RoseController.attributeAffects(RoseController.crownWidth,  RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.probScale = nAttr.create('probScale', 'ps', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.probScale)
        RoseController.attributeAffects(RoseController.probScale,  RoseController.output)

        nAttr = om.MFnNumericAttribute()
        RoseController.inclRatio = nAttr.create('inclRatio', 'ir', om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.hidden = False
        RoseController.addAttribute(RoseController.inclRatio)
        RoseController.attributeAffects(RoseController.inclRatio,  RoseController.output)

        RoseController.shootDirs = [None] * 10
        for i in range(10):
            nAttr = om.MFnNumericAttribute()
            RoseController.shootDirs[i] = nAttr.create('shoot' + str(i), 'td' + str(i), om.MFnNumericData.k3Double, 0.0)
            nAttr.writable = True
            nAttr.keyable = True
            nAttr.hidden = False
            RoseController.addAttribute(RoseController.shootDirs[i])
            RoseController.attributeAffects(RoseController.shootDirs[i],  RoseController.output)


def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject, vendor = 'MukaiLab', version = '0.1')
    try:
        mplugin.registerCommand(RoseBuild.kCmdName, RoseBuild.creator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % RoseBuild.kCmdName)
        raise
    try:
        mplugin.registerCommand(RoseRegenerate.kCmdName, RoseRegenerate.creator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % RoseRegenerate.kCmdName)
        raise
    try:
        mplugin.registerNode(
            RoseController.kNodeName,
            RoseController.kNodeId,
            RoseController.creator,
            RoseController.initializer,
            om.MPxNode.kDependNode,
            'utility/general')
    except:
        sys.stderr.write('Failed to register node: %s' % RoseController.kNodeName)
        raise


def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(RoseBuild.kCmdName)
    except:
        sys.stderr.write("Failed to deregister command: %s\n" % RoseBuild.kCmdName)
        raise
    try:
        mplugin.deregisterCommand(RoseRegenerate.kCmdName)
    except:
        sys.stderr.write("Failed to deregister command: %s\n" % RoseRegenerate.kCmdName)
        raise
    try:
        mplugin.deregisterNode(RoseController.kNodeId)
    except:
        sys.stderr.write('Failed to deregister node: %s' % RoseController.kNodeName)
        raise
