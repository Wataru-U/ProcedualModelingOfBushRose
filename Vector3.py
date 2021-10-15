import math
import copy

class Vector3(object) :
    def __init__(self,x,y,z) :
        self.x = x
        self.y = y
        self.z = z
    
    def Vector(self) :
        '''Maya の Curve の頂点に合わせたデータで返す'''
        return (self.x,self.y,self.z)

    def Normalize(self) :
        '''自身のベクトルを正規化する'''
        sc = abs(self)
        sc = math.sqrt(sc)
        if not sc == 0 :
            self.x /= sc
            self.y /= sc
            self.z /= sc
        return self

    def Normalized(a) :
        '''　a を正規化したベクトルを返す '''
        v = copy.copy(a)
        v.Normalize()
        return v

    def Dot(self,other) :
        '''self と other の内積を返す'''
        x = self.x * other.x
        y = self.y * other.y
        z = self.z * other.z
        return x + y + z
    
    def Cross(self,other) :
        ''' self と other の外積を返す'''
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector3(x,y,z)
    
    def Vertical_xz(self,other) :
        '''self と直交する other の xz を固定した ベクトルを返す''' 
        # ０で割るのを避ける
        if self.y == 0 :
            if self.x * other.x + self.z * other.z == 0 :
                return Vector3(other.x,0,other.z).Normalize()
            else :
                return Vector3(0,1,0)
        y = - (self.x * other.x + self.z * other.z) / self.y
        return Vector3(other.x,y,other.z)


    def WeightedAverage(self,other,selfWeight,otherWeight) :
        '''ベクトルの加重平均を返す'''
        return (self * selfWeight + other * otherWeight) / (selfWeight + otherWeight)

    def Normalized_hv(hori,vert) :
        return Vector3(math.cos(hori) * math.cos(vert),math.sin(vert),math.sin(hori) * math.cos(vert))

    def __add__(self, other) :
        """+ 演算子を定義するメソッド
            要素同士を足し合わせた新しい Vector3 インスタンスを返す """
        return Vector3(self.x + other.x,self.y + other.y ,self.z + other.z)

    def __sub__(self, other) :
        """- 演算子を定義するメソッド
            要素同士を引き合わせた新しい Vector3 インスタンスを返す """
        return Vector3(self.x - other.x,self.y - other.y ,self.z - other.z)

    def __mul__(self, scalar) :
        """* 演算子を定義するメソッド
           要素に scalar をかけた新しい Vector3 インスタンスを返す """
        return Vector3(self.x * scalar,self.y * scalar,self.z * scalar)

    def __truediv__(self, scalar) :
        """/ 演算子を定義するメソッド
           要素に scalar を割った新しい Vector3 インスタンスを返す """
        return Vector3(self.x / scalar,self.y / scalar,self.z / scalar)

    def __abs__(self) :
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def __eq__(self, other) :
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other) :
        return not (self.x == other.x and self.y == other.y and self.z == other.z)
