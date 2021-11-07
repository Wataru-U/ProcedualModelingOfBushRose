import pymel.core as pm
import math
import random
import Vector3 as v3



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

    def NewBranchDir(self,theta) :
        ''' 新しい枝の向きを決める　'''
        # 節の Dir を y 、　pos.xz を x として
        # 株の外側を 0 とした正規直交基底を作る
        base_x = v3.Vector3.Normalized(self.Pos)
        base_y = self.Dir
        base_x = v3.Vector3.Normalized(base_y.Vertical_xz(base_x))
        base_z = base_x.Cross(base_y)
        
        # 規定を変える前のベクトル
        d = v3.Vector3(0,0,0)
        d.x = math.cos(theta) * math.cos(self.LeafDir)
        d.y = math.sin(theta)
        d.z = math.cos(theta) * math.sin(self.LeafDir)


        # 規定を変換した新しい枝の向き
        result = v3.Vector3(0,0,0)
        result += base_x * d.x
        result += base_y * d.y
        result += base_z * d.z

        return result

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
        else :
            branch.Vertices.append(self.tip())

# 一般の枝の節クラス
class OldBranchSection(Section) :
    def __init__(self, p, d, dist, l, inc, s, e, branch, ph, pw, sn, lSeed=-1, bSeed=-1):
        super().__init__(p, d, dist, l, inc, s, e, branch, lSeed=lSeed, bSeed=bSeed)

        self.PruneHeight = ph
        self.PruneWidth = pw
        self.SectionNum = sn
        # 次の節を出すかどうか
        dist_xz = (p.x ** 2 + p.z ** 2) / pw ** 2
        dist_y = p.y ** 2 / ph ** 2

        # 剪定範囲内 かつ 花がらつみ範囲内　か
        # 節が短すぎると カーブ が成り立たないので, 短すぎる場合, 剪定範囲超えても少し出す
        if dist <= sn and dist_xz + dist_y <= 1 :
            nextDir = \
                v3.Vector3.WeightedAverage(d,self.IdealDir,self.Strength,dist ** self.WeightExponent) \
                if math.tan(inc) > self.DirInc_y_xz \
                else d
            branch.Append(self.tip(),nextDir,dist+1,l,ph,pw,inc,s,e)
        else :
            # 剪定範囲を超えたら
            if dist_xz + dist_y > 1 :
                branch.Next = False
            branch.Vertices.append(self.tip())

# 花枝の節クラス
class NewBranchSection(Section) :
    def __init__(self, p, d, dist, l, inc, s, e, branch, sn, lSeed=-1, bSeed=-1):
        super().__init__(p, d, dist, l, inc, s, e, branch, lSeed=lSeed, bSeed=bSeed)

        self.SectionNum = sn

        if dist <= sn :
            nextDir = \
                v3.Vector3.WeightedAverage(d,self.IdealDir,self.Strength,dist ** self.WeightExponent) \
                if math.tan(inc) > self.DirInc_y_xz \
                else d
            branch.Append(self.tip(),nextDir,dist+1,l,inc,s,e)
        else :
            branch.Vertices.append(self.tip())

        
class RoseBranch :
    def __init__(self,p,d,dist,sl,inc,s,e,prob,fprob,lh,cs,hs,thi,tree,rand = True,name = 'Branch'):
        self.Vertices = [p,p.WeightedAverage(p + d * sl,100,1)]
        self.Pos = p
        self.Dir = d
        self.Dist = dist
        self.SectionLength = sl
        self.Inclination = inc
        self.Strength = s
        self.WeightExponent = e
        self.Probability = prob
        self.FlowerBranchProbability = fprob
        self.LowestHeight = lh
        self.Name = name
        self.Sections = []

        self.Tree = tree

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
        それ以外は螺旋状風に 
        '''
        leafDir = 0
        for i in range(len(self.Sections)) :
            index = i
            item = self.Sections[index]
            '''
            # 2/5葉序
            # ランダムの振れ幅
            leafDirRange = math.pi / 3 * 2
            leafDir = leafDir + (item.LeafSeed - 0.5) * leafDirRange 
            '''
            item.SetLeafDir(leafDir)

            # 次の枝の向き
            # 花がら摘みで出たら /6 春先なら /2
            theta = math.pi / 6 if i <= 1 else math.pi / 2
            nd = item.NewBranchDir(theta)
            # 先端は下を向かないようにする
            if i == 0 :
                while nd.y < 0 :
                    leafDir += math.pi / 3
                    item.SetLeafDir(leafDir)
                    nd = item.NewBranchDir(math.pi / 6)
            leafDir += math.pi / 4 * 3


class ShootBranch(RoseBranch) :
    def __init__(self, p, d, dist, sl, inc, s, e, prob, fprob, lh, cs, hs, thi, ph, pw, tree, rand=True):
        super().__init__(p, d, dist, sl, inc, s, e, prob, fprob, lh, cs, hs, thi, tree, rand=rand, name = 'Shoot')
        self.PinchHeight = ph
        self.PinchWidth = pw

        # 節を追加していく
        self.Sections.append(ShootSection(p,d,1,sl,ph,pw,inc,s,e,self))
        # 葉と次の枝をセット
        self.SetLeaves()
        for i in range(len(self.Sections)) :
            index = i
            item = self.Sections[index]
            # 次の枝の向き
            # 花がら摘みで出たら pi/3 春先なら 0
            theta = math.pi / 3 if i <= 1 else 0
            nd = item.NewBranchDir(theta)

            # 剪定ラインからの割合
            prune_xz = (item.Pos.x ** 2 + item.Pos.z ** 2) / (tree.PruneWidth ** 2)
            prune_y = (item.Pos.y ** 2) / (tree.PruneHeight ** 2)
            prune = prune_xz + prune_y

            if (i <= 1 or item.BranchSeed * 100 < self.Probability) and nd.y  > 0 :
                tree.Branches.append( \
                    OldBranch \
                        (item.Pos,nd,1,tree.BranchSectionLength,self.Inclination,self.Strength,self.WeightExponent, \
                        self.Probability,self.FlowerBranchProbability,self.LowestHeight,self.CircleSmoothness,tree.BranchSmoothness,tree.BranchThickness, \
                        tree.PruneHeight,tree.PruneWidth,tree.BranchSectionNum,tree,rand))
            elif item.BranchSeed * 100 < self.Probability + self.FlowerBranchProbability and nd.y > 0 and prune > self.LowestHeight ** 2 :
                tree.Branches.append(NewBranch(item.Pos,nd,dist+1,tree.FlowerSectionLength,self.Inclination,self.Strength,self.WeightExponent,\
                        self.Probability,self.CircleSmoothness,tree.Flowersmoothness,tree.FlowerThickness,\
                        tree.FlowerSectionNum,tree,rand))

    
    def Append(self,tip,nd,dist,l,ph,pw,inc,s,e) :
        '''節を引数に引数の節を リストに 追加する'''
        self.Vertices.append(tip)
        self.Sections.append(ShootSection(tip,nd,dist,l,ph,pw,inc,s,e,self))

class OldBranch(RoseBranch) :
    def __init__(self, p, d, dist, sl, inc, s, e, prob,fprob,lh, cs, hs, thi, ph, pw, sn, tree, rand=True, name='Branch'):
        super().__init__(p, d, dist, sl, inc, s, e, prob,fprob,lh, cs, hs, thi, tree, rand=rand, name=name)
        self.PruneHeight = ph
        self.PruneWidth = pw
        self.SectionNum = sn
        # 花がら摘みで新しい枝が出るかどうか
        self.Next = True

        # 節を追加していく
        self.Sections.append(OldBranchSection(p,d,0,sl,inc,s,e,self,ph,pw,sn))
        self.SetLeaves()
        for i in range(len(self.Sections)) :
            index = i
            item = self.Sections[index]
            # 次の枝の向き
            # 花がら摘みで出たら pi/3 春先なら 0
            theta = math.pi / 3 if i <= 1 else 0
            nd = item.NewBranchDir(theta)

            # 剪定ラインからの割合
            prune_xz = (item.Pos.x ** 2 + item.Pos.z ** 2) / (self.PruneWidth ** 2)
            prune_y = (item.Pos.y ** 2) / (self.PruneHeight ** 2)
            prune = prune_xz + prune_y

            if ((i <= 1 and self.Next) or item.BranchSeed * 100 < self.Probability) and nd.y  > 0 and dist < 4:
                nb = OldBranch \
                        (item.Pos,nd,dist+1,tree.BranchSectionLength,self.Inclination,self.Strength,self.WeightExponent, \
                        self.Probability,self.FlowerBranchProbability,self.LowestHeight,self.CircleSmoothness,tree.BranchSmoothness,tree.BranchThickness, \
                        tree.PruneHeight,tree.PruneWidth,tree.BranchSectionNum,tree,rand)
                # カーブとして成り立たない場合は入れない
                if len(nb.Vertices) > 3 :
                    tree.Branches.append(nb)
            elif (i <= 1 and not self.Next) or item.BranchSeed * 100 < self.Probability + self.FlowerBranchProbability and nd.y > 0 and prune > self.LowestHeight ** 2 :
                tree.Branches.append(NewBranch(item.Pos,nd,dist+1,tree.FlowerSectionLength,self.Inclination,self.Strength,self.WeightExponent,\
                        self.Probability,self.CircleSmoothness,tree.Flowersmoothness,tree.FlowerThickness,\
                        tree.FlowerSectionNum,tree,rand))

    def Append(self,tip,nd,dist,l,ph,pw,inc,s,e) :
        '''節を引数に引数の節を リストに 追加する'''
        self.Vertices.append(tip)
        self.Sections.append(OldBranchSection(tip,nd,dist,l,inc,s,e,self,ph,pw,self.SectionNum))

class NewBranch(RoseBranch) :
    def __init__(self, p, d, dist, sl, inc, s, e, prob, cs, hs, thi, sn, tree, rand=True, name='NewBranch'):
        super().__init__(p, d, dist, sl, inc, s, e, prob, 0, 0, cs, hs, thi, tree, rand=rand, name=name)

        self.SectionNum = sn
         # 節を追加していく
        self.Sections.append(NewBranchSection(p,d,0,sl,inc,s,e,self,sn))
        self.SetLeaves()

    def Append(self,tip,nd,dist,l,inc,s,e) :
        '''節を引数に引数の節を リストに 追加する'''
        self.Vertices.append(tip)
        self.Sections.append(NewBranchSection(tip,nd,dist,l,inc,s,e,self,self.SectionNum))

class BushRoseTree :
    def __init__(self,name,cs,inc,s,e,prob,fprob,lh,sph,spw,ssl,st,ss,sn,bph,bpw,bsn,bsl,bt,bs,fnum,fneck,g,fsn,fsl,ft,fs,rand = True):
        # 共有部分
        # 軸の分割
        self.Name = name
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
            self.Branches.append(ShootBranch(v3.Vector3(0,0,0),vec,0,ssl,inc,s,e,prob,fprob,lh,cs,ss,st,sph,spw,self))
        
        # モデル用
        self.Curves = []
        self.Cils = []
        

    def CreateCurve(self) :
        '''カーブを作る'''

        # 初期化
        self.Curves = []
        self.Cils = []
        i = 0
        for item in self.Branches :
                name = item.Name + '_' + str(i) + '_'
                self.Curves.append(pm.curve(name = name + 'CUR',p = [j.Vector() for j in item.Vertices]))
                i += 1

        # オブジェクトの名前
        name = self.Name if not self.Name == '' else 'BushRose'
        # グループにして行く
        pm.select(self.Curves)
        self.CurvesGRP = pm.group(n = name + '_Curves_GRP')
        pm.select(self.CurvesGRP)
        self.group = pm.group(n = name + '_GRP')

    def SetMesh(self) :
        '''カーブにメッシュを付ける'''
        # カーブがない場合
        if len(self.Curves) == 0 :
            self.CreateCurve()
        self.Cils = []
        
        i = 0
        for item in self.Branches :
            name = item.Name + '_' + str(i) + '_'
            self.Cils.append(pm.polyCylinder(name = name + 'GEO',r = item.Thickness,h = 400,sx = item.CircleSmoothness,sy = item.HeightSmoothness * len(item.Sections)))
            pm.createCurveWarp(self.Curves[i],self.Cils[i])
            i += 1
        
        # シリンダーのエッジをきれいにする
        for item in self.Cils :
            cilSoftEdge(item)
        
        # グループにまとめる
        name = self.Name if not self.Name == '' else 'BushRose'
        pm.select(self.Cils)
        self.CilsGRP = pm.group(n = name + '_Cils_GRP')
        pm.parent(self.CilsGRP,self.group)
    
    def SetLeaves(self,leaf_obj_name) :
        self.Leaves = []
        find_obj = pm.ls(leaf_obj_name)
        if len(find_obj) == 0 :
            # 葉のオブジェクトが見つからない場合エラー
            pm.error(u'object \'{name}\' not found'.format(name = leaf_obj_name))
        else :
            for item in self.Branches :
                if type(item) == NewBranch :
                    print(item.Name)
                    for i in range(len(item.Sections)) :
                        sec = item.Sections[i]

                        # 節の Dir を y 、　pos.xz を x として
                        # 株の外側を 0 とした正規直交基底を作る
                        base_x = v3.Vector3.Normalized(sec.Pos)
                        base_y = sec.Dir
                        base_x = v3.Vector3.Normalized(base_y.Vertical_xz(base_x))
                        base_z = base_x.Cross(base_y)
                        # 葉の向きに合わせる
                        theta = sec.LeafDir
                        temp = base_x * math.cos(theta) + base_z * math.sin(theta)
                        base_z = base_x * (-math.sin(theta)) + base_z * math.cos(theta)
                        base_x = temp

                        # 葉のオブジェクトを複製
                        obj = pm.duplicate(leaf_obj_name)

                        # 名前と超点数の取得
                        pm.select(obj)
                        obj_name = pm.ls(sl = True)
                        l = (pm.polyEvaluate(v = True))
                        
                        # 頂点を移動していく
                        for i in range(l) :
                            vert_index = '.vtx[' + str(i) + ']'
                            vert_name = obj_name[0].replace('Shape','') + vert_index
                            pm.select(vert_name)
                            # 頂点を取得
                            vert_pos_list = pm.pointPosition()
                            # Vector3 に変換
                            vert_pos = v3.Vector3(vert_pos_list[0],vert_pos_list[1],vert_pos_list[2])
                            # 新しい基底に変換
                            new_pos = base_x * vert_pos.x + base_y * vert_pos.y + base_z * vert_pos.z

                            # 頂点を移動
                            pm.move(new_pos.x,new_pos.y,new_pos.z)
                        
                        # モデルを移動
                        pm.select(obj)
                        pm.move(sec.Pos.x,sec.Pos.y,sec.Pos.z)

                        self.Leaves.append(obj)
            # グループにまとめる
            name = self.Name if not self.Name == '' else 'BushRose'
            pm.select(self.Leaves)
            self.LeavesGRP = pm.group(n = name + '_Leaves_GRP')
            pm.parent(self.LeavesGRP,self.group)







def cilSoftEdge(obj) :
    '''シリンダーの 上面底面 以外をソフトエッジにする'''
    pm.select(obj)
    # 全体をソフトエッジに
    pm.polySoftEdge(a = 180,ch = 1)
    pm.select(obj)
    # フェースの数を取る
    l = (pm.polyEvaluate(f = True))
    # オブジェクトの名前
    objName = pm.ls(sl = True)
    faceNum = '.f[' + str(l-2) + ':' + str(l-1) + ']'
    # シリンダーの上下をハードエッジに
    pm.select(objName[0].replace('Shape','') + faceNum)
    pm.polySoftEdge(a = 0,ch = 1)

