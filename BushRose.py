import pymel.core as pm
import math
import random
import Vector3 as v3
from pymel.core.windows import horizontalLayout


# 基底節クラス
class Section :
    def __init__(self, p, d, dist, l, inc, s, e, branch, lSeed = -1., bSeed = -1.) :
        # 位置
        self.Pos = p
        # 方向
        self.Dir = d
        # 枝の根元からの距離
        self.Dist = dist
        # 節の長さ cm
        self.Length = l
        # 傾きの目安
        self.Inclination = inc
        # 曲がりにくさ
        self.Strength = s
        # 枝の重みの指数部
        self.WeightExponent = e
        # ランダムシード
        self.LeafSeed = lSeed if not lSeed == -1. else random.random()
        self.BranchSeed = bSeed if not bSeed == -1. else random.random()
        # 親の枝
        self.Branch = branch
        # 葉の向き 後で決めるのでとりあえず 0   0 ~ 1
        self.LeafDir = 0

        # 傾きと Dir の xz　に合わせた理想的なベクトルを求める
        mag_xz = math.sqrt(d.x ** 2 + d.z ** 2)
        ideal_x = d.x * math.cos(inc) / mag_xz
        ideal_z = d.z * math.cos(inc) / mag_xz
        self.DirInc_y_xz = d.y / mag_xz
        self.IdealDir = v3.Vector3(ideal_x,abs(math.sin(inc)),ideal_z)

     
    def tip(self) :
        '''先端の位置を返す'''
        return self.Pos + self.Dir * self.Length
    
    def SetLeafDir(self,d) :
        self.LeafDir = d


# シュートの節クラス
class ShootSection(Section) :
    def __init__(self, p, d, dist, l, ph, pw, inc, s, e, branch):
        super().__init__(p, d, dist, l, inc, s, e, branch)
        # ピンチする高さ
        self.PinchHeight = ph
        # ピンチする幅
        self.pinchWidth = pw
        
        # 次の節を出すかどうか
        dist_xz = (p.x ** 2 + p.z ** 2) / pw ** 2
        dist_y = p.y ** 2 / ph ** 2
        # ピンチ範囲内だったら
        if dist_xz + dist_y <= 1 :
            # 理想の傾きより大きくない場合
            # 根元からの節の数に合わせた 加重平均を取る
            nextDir = \
                v3.Vector3.WeightedAverage(d,self.IdealDir,self.Strength,dist ** self.WeightExponent) \
                if math.tan(inc) > self.DirInc_y_xz \
                else d
            branch.Append(self.tip(),nextDir,dist+1,l,ph,pw,inc,s,e)



class RoseBranch :
    def __init__(self,p,d,dist,sl,inc,s,e,cs,hs,thi,rand = True,name = 'Branch'):
        self.Vertices = [p,p.WeightedAverage(p + d * sl,100,1)]
        self.Pos = p
        self.Dir = d
        self.Dist = dist
        self.SectionLength = sl
        self.Inclination = inc
        self.Strength = s
        self.WeightExponent = e
        self.Name = name
        self.Sections = []

        # 軸と高さの分割
        self.CircleSmoothness = cs
        self.HeightSmoothness = hs
        # 太さ
        self.Thickness = thi
        self.Random = rand
    
    def SetLeaves(self) :
        ''' 葉の位置や枝が出るかどうか
        先端の節から行う
        先端は基本外側を向く
        それ以外は螺旋状風に '''
        leafDir = 0
        for i in range(len(self.Sections)) :
            index = len(self.Sections) - i - 1
            item = self.Sections[index]
            # ランダムの振れ幅
            leafDirRange = math.pi / 3 * 2
            leafDir = leafDir + (item.LeafSeed - 0.5) * leafDirRange 
            item.SetLeafDir(leafDir)
            leafDir += math.pi / 2


class ShootBranch(RoseBranch) :
    def __init__(self, p, d, dist, sl, inc, s, e, cs, hs, thi, ph, pw, rand=True):
        super().__init__(p, d, dist, sl, inc, s, e, cs, hs, thi, rand=rand, name = 'Shoot')
        self.PinchHeight = ph
        self.PinchWidth = pw

        # 節を追加していく
        self.Sections.append(ShootSection(p,d,1,sl,ph,pw,inc,s,e,self))
        # 葉と次の枝をセット
        self.SetLeaves()

    
    def Append(self,tip,nd,dist,l,ph,pw,inc,s,e) :
        '''節を引数に引数の節を リストに 追加する'''
        self.Vertices.append(tip)
        self.Sections.append(ShootSection(tip,nd,dist,l,ph,pw,inc,s,e,self))

class BushRoseTree :
    def __init__(self,cs,inc,s,e,prob,lh,sph,spw,ssl,st,ss,sn,bph,bpw,bsn,bsl,bt,bs,fnum,fneck,g,fsn,fsl,ft,fs,rand = True):
        # 共有部分
        # 軸の分割
        self.CircleSmoothness = cs
        # 傾き
        self.Inclination = inc
        # 曲がりにくさ
        self.Strength = s
        # 重みの指数部
        self.WeigthtExponent = e
        # 枝の出やすさ
        self.Probability = prob
        # 新しい枝の一番下の高さの割合
        self.LowestHeight = lh
        # シュートの数
        self.ShootNum = sn
        # ランダムの有無
        self.Random = rand

        # シュート
        self.PinchHeight = sph
        self.PichWidth = spw
        self.ShootSectionLength = ssl
        self.Shootthickness = st
        self.ShootSommthness = ss

        # 古い一般的な枝
        self.PruneHeight = bph
        self.PruneWidth = bpw
        self.BranchSectionNum = bsn
        self.BranchSectionLength = bsl
        self.BranchThickness = bt
        self.BranchSmoothness = bs

        # 花枝
        self.FlowerNum = fnum
        self.FloerNeck = fneck
        self.Gravity = g
        self.FlowerSectionNum = fsn
        self.FlowerSectionLength = fsl
        self.FlowerThickness = ft
        self.Flowersmoothness = fs

        # 枝の追加
        self.Branches = []
        for i in range(self.ShootNum) :
            hori = random.random() * 2 * math.pi
            vert = random.random() * math.pi / 2
            vec = v3.Vector3.Normalized_hv(hori,vert)
            self.Branches.append(ShootBranch(v3.Vector3(0,0,0),vec,0,ssl,inc,s,e,cs,ss,st,sph,spw))

    def CreateCurve(self) :
        '''モデルを作る'''
        self.Curves = []
        self.Cils = []
        i = 0
        for item in self.Branches :
            name = item.Name + '_' + str(i) + '_'
            self.Curves.append(pm.curve(name = name + 'CUR',p = [i.Vector() for i in item.Vertices]))
            self.Cils.append(pm.polyCylinder(name = name + 'GEO',r = item.Thickness,h = 400,sx = item.CircleSmoothness,sy = item.HeightSmoothness * len(item.Sections)))
            pm.createCurveWarp(self.Curves[i],self.Cils[i])
            i += 1
