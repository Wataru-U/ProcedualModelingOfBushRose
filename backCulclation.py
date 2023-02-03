# window の　 slider の値は getValue()

import pymel.core as pm
import math
import Vector3 as v3
import BushRose as br

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
        
        # ランダム要素　の有無
        # ランダムをなくすと同じパラメータに対していつも同じモデルを返す　予定


        pm.showWindow(self.window)

    # ちょうどいい高さを２部探索で探す
    def heightBinarySearch(self, upperLimit, LowerLimit) :
        print(upperLimit,LowerLimit)
        h = (upperLimit + LowerLimit) / 2
        if upperLimit - LowerLimit <= 5 :
            self.pruneHeight = h
            self.pinchHeight = max(10,h/2)
        else :
            self.Tree(h,self.Width.getValue(),max(10,h/2),max(10,self.Width.getValue()))
            if self.Height.getValue() < self.brt.Top() :
                self.heightBinarySearch(h,LowerLimit)
            else :
                self.heightBinarySearch(upperLimit,h)

    def widthBinarySearch(self, upperLimit, LowerLimit) :
        print(upperLimit,LowerLimit)
        w = (upperLimit + LowerLimit) / 2
        if upperLimit - LowerLimit <= 5 :
            self.pruneWidth = w
            self.pinchWidth = max(10,w/2)
        else :
            self.Tree(self.pruneHeight,w,max(10,self.pruneHeight/2),max(10,w/2))
            if self.brt.isLarge(self.Height.getValue(),self.Width.getValue()) :
                self.widthBinarySearch(w,LowerLimit)
            else :
                self.widthBinarySearch(upperLimit,w)

    # curveを作る
    # 引数の *args コマンドとして扱う用
    def CreateCurve(self,*args) :
        self.heightBinarySearch(self.Height.getValue(), 10)
        self.widthBinarySearch(self.Width.getValue(), 10)
        self.Tree(self.pruneHeight,self.pruneWidth,self.pinchHeight,self.pinchWidth)
        self.brt.CreateCurve()
    
    def Tree(self, pruneHeight,pruneWidth,pinchHeight,pinchWidth) :
        self.brt = br.BushRoseTree \
            ( \
                pm.textField(self.Name, q=True, text=True), \
                self.Smoothness.getValue(), self.Inclination.getValue(), self.Strength.getValue(), self.WeightExponent.getValue(), self.Probability.getValue(), self.FlowerBranchProbability.getValue(), self.LowestHeight.getValue(), self.KillDiff.getValue(),\
                pinchHeight, pinchWidth, self.ShootParam.sectionLength.getValue(), self.ShootParam.thickness.getValue(), self.ShootParam.smoothness.getValue(), self.ShootParam.shootNum.getValue(), \
                pruneHeight, pruneWidth, self.BranchParam.sectionNum.getValue(), self.BranchParam.sectionLength.getValue(), self.BranchParam.thickness.getValue(), self.BranchParam.smoothness.getValue(), \
                self.FlowerBParam.flowerNum.getValue(), self.FlowerBParam.gravity.getValue(), \
                self.FlowerBParam.sectionNum.getValue(), self.FlowerBParam.sectionLength.getValue(), self.FlowerBParam.thickness.getValue(), self.FlowerBParam.smoothness.getValue(), self.FlowerStrength.getValue(),self.FlowerWeightExponent.getValue(), \
            )

    # メッシュをつける
    def CreateMesh(self,*args) :
        if self.brt == None :
            self.brt = br.BushRoseTree_Cube \
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


roseParam = RoseParameter()
