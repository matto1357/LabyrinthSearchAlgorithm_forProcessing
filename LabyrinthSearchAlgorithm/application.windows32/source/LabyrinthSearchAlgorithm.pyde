import random
import copy

#----------設定用の変数----------

#マップの大きさを指定する
#x,yそれぞれ5以上の奇数にすること
#このサイズには外壁も含むので実質的な大きさはX,Yそれぞれ-2
mapSizeX = 27
mapSizeY = 27

#マップ1マス(正方形)の大きさ
mapChipSize = 15
#マップの端の大きさ
mapSideSize = 10
#テキストエリア
textAreaSizeY = 30

#スタートとゴールの決め方
# 0→ランダム生成
# 1→左上スタート右下ゴール
# 2→左下スタート右下ゴール
pointMode = 0

#アニメーションモード
# 0→なし
# 1→壁生成のみ
# 2→探索のみ
# 3→壁生成と探索
animMode = 3

#探索のアニメーションモード(未実装)
# 0→step内一斉表示
# 1→step内を1つずつ表示
animSolveMode = 1

#アニメーションのスピード(delay)
animKabeDelay = 50
animSolveDelay = 80

#アニメーションの間隔
animNextDelay = 3000

#----------変数----------

#マップデータ
mapData = []
#柱
columnList = []

#方向
dir = []
topdir = []

#スタート地点
startPos = None
#ゴール地点
goalPos = None

#道リスト
#スタート地点とゴール地点のランダム生成用
floorList = []

#探索手順を保持しておく
#次の探索候補
solveResult = []
#全部の探索結果
solveHistory = []
#解法
trueSolve = None

#探索手順の識別用ID
id = 1

#探索が終了したかどうか
isSolveCompleted = False

#ターン数
turn = 1

#テキスト表示用
textAreaY = mapSizeY * mapChipSize + mapSideSize * 2

#----------アニメーション用----------

#壁
animKabe = []
animKabeNum = 0
isAnimKabeEnd = False
#探索
animSolvestepNum = 0
animSolveinStepNum = 0
isAnimSolveEnd = False

#----------クラス----------

#ポジションクラス
class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
#探索手順を保持するクラス
class SolveHistory:
    def __init__(self):
        global id
        self.id = id
        id += 1
        self.path = []
    #ポジションを追加して、pathを更新する
    def Add(self, pos):
        self.x = pos.x
        self.y = pos.y
        self.SetID()
        if(self.GoalCheck() == False):
            self.path.append(pos)
            global isAnimSolveEnd
            if(isAnimSolveEnd):
                SetMapData(self.x, self.y, 4)
            else:
                SetMapData(self.x, self.y, 14)
    #ID更新
    def SetID(self):
        global id
        self.id = self.id * 10 + id 
        id = id + 1
    #ゴール地点に着いたか確認する
    def GoalCheck(self):
        if(self.x == goalPos.x and self.y == goalPos.y):
            global isSolveCompleted
            isSolveCompleted = True
            SolveHighLight(self)
            return True
        return False
    
#----------関数----------

#初期化
def Init():
    #dirとtopdirの初期化
    pos = Pos(0, -1)
    topdir.append(pos)
    pos = Pos(1, 0)
    dir.append(pos)
    topdir.append(pos)
    pos = Pos(0, 1)
    dir.append(pos)
    topdir.append(pos)
    pos = Pos(-1, 0)
    dir.append(pos)
    topdir.append(pos)
    
    #アニメーションの初期化
    global animMode
    global isAnimKabeEnd
    global isAnimSolveEnd
    if(animMode == 0):
        isAnimKabeEnd = True
        isAnimSolveEnd = True
    elif(animMode == 1):
        isAnimKabeEnd = False
        isAnimSolveEnd = True
    elif(animMode == 2):
        isAnimKabeEnd = True
        isAnimSolveEnd = False
    elif(animMode == 3):
        isAnimKabeEnd = False
        isAnimSolveEnd = False

#マップを生成する
def MapInit(_x, _y):
    global mapData
    #リストを作る
    for y in range(_y):
        _map = []
        for x in range(_x):
            #外壁を作成
            if(y == 0 or y == mapSizeY - 1 or x == 0 or x == mapSizeX - 1):
                _map.append(1)
            #柱を作成
            elif(x % 2 == 0 and y % 2 == 0):
                _map.append(1)
                pos = Pos(x, y)
                columnList.append(pos)
            #道を作成
            else:
                _map.append(0)
                pos = Pos(x, y)
        mapData.append(_map)

#壁の自動生成
#棒倒し法で生成
def MapMake():
    for pos in columnList:
        candidate = []
        dirs = []
        
        if(pos.y == 2):
            dirs = topdir
        else:
            dirs = dir
            
        for _dir in dirs:
            x = pos.x + _dir.x
            y = pos.y + _dir.y
            if(GetMapData(x, y) == 0):
                _pos = Pos(x, y)
                candidate.append(_pos)
        _pos = random.choice(candidate)
        if(isAnimKabeEnd):
            SetMapData(_pos.x, _pos.y, 1)
        else:
            SetMapData(_pos.x, _pos.y, 11)
            animKabe.append(_pos)
                
#指定された座標のマップ情報を返す
def GetMapData(x, y):
    return mapData[y][x]

#指定された座標のマップ情報を引数の値にセットする
def SetMapData(x, y, _map):
    mapData[y][x] = _map
    
#道の中から1つを選択
#引数をTrueにすると、選ばれた値を再び選ばれないようにする
def GetRandomPos(isdelete = False):
    pos = random.choice(floorList)
    if(isdelete == True):
        floorList.remove(pos)
    return pos

#道を取得
def GetFloor(data):
    for y in range(mapSizeY):
        for x in range(mapSizeX):
            chip = GetMapData(x, y)
            if(chip == 0):
                pos = Pos(x, y)
                floorList.append(pos)

#スタートとゴールをセットする
#引数に0を入れるとランダム生成
#引数に1を入れると左上スタート右下ゴール
#引数に2を入れると左下スタート右下ゴール
def SetPoint(mode):
    global startPos
    global goalPos
    if(mode == 0):
        startPos = GetRandomPos(True)
        goalPos = GetRandomPos(True)
    elif(mode == 1):
        startPos = Pos(1, 1)
        goalPos = Pos(mapSizeX - 2, mapSizeY - 2)
    elif(mode == 2):
        startPos = Pos(1, mapSizeY - 2)
        goalPos = Pos(mapSizeX - 2, mapSizeY - 2)
        
    SetMapData(startPos.x, startPos.y, 2)
    SetMapData(goalPos.x, goalPos.y, 3)


#迷路を解く
#幅優先を使用
def Solve():
    global solveResult
    global id
    global isSolveCompleted
    global turn
    
    GetFloor(mapData)
    SetPoint(pointMode)
    
    print("StartPos:" , startPos.x, startPos.y)
    print(" ")
    
    #1手目
    for _dir in topdir:
        solve = None
        x = startPos.x + _dir.x
        y = startPos.y + _dir.y
        chip = GetMapData(x, y)
        if(chip == 0 or chip == 3):
            solve = SolveHistory()
            pos = Pos(x, y)
            solve.Add(pos)
            solveResult.append(solve)
    #PrintSolve(turn)
    #print("step:" + str(turn) + " count:" + str(len(solveResult)))
    turn = turn + 1
    solveHistory.append(solveResult)
    
    #2手目以降
    while(isSolveCompleted == False):
        newSolve = []
        for solve in solveResult:
            id = 1
            dirList = []
            for _dir in topdir:
                x = solve.x + _dir.x
                y = solve.y + _dir.y
                chip = GetMapData(x, y)
                if(chip == 0 or chip == 3):
                    dirList.append(_dir)
            for _dir in dirList:
                pos = Pos(solve.x + _dir.x, solve.y + _dir.y)
                _solve = copy.deepcopy(solve)                
                _solve.Add(pos)
                newSolve.append(_solve)
        solveResult = newSolve
        #PrintSolve(turn)
        #print("step:" + str(len(solveHistory)) + " count:" + str(len(solveResult)))
        turn = turn + 1
        solveHistory.append(solveResult)

#デバッグ用に手順をコンソールに出力
def PrintSolve(th):
    print("Turn" , th)
    print("----------")
    for solve in solveResult:
            print("id:" , solve.id)
            for path in solve.path:
                print(path.x, path.y)
            print("-----")
    print(" ")

#解法をハイライト表示
def SolveHighLight(_solve):
    global turn
    global trueSolve
    trueSolve = _solve
    print("Turn" , len(trueSolve.path))
    if(isAnimSolveEnd):
        for pos in _solve.path:
            SetMapData(pos.x, pos.y, 6)
    
#マップを描画する
def MapDraw(data):
    stroke(128)
    strokeWeight(2)
    for y in range(mapSizeY):
        for x in range(mapSizeX):
            chip = GetMapData(x, y)
            
            #道(未探索)
            if(chip == 0):
                fill(255)
            #壁
            elif(chip == 1):
                fill(0)
            #スタート地点
            elif(chip == 2):
                fill(255,0,0)
            #ゴール地点
            elif(chip == 3):
                fill(32,64,255)
            #道(探索済)
            elif(chip == 4):
                fill(160,160,160)
            #道(探索済かつ死に道)
            elif(chip == 5):
                fill(224,224,224)
            #解
            elif(chip == 6):
                fill(0,255,0)
            else:
                fill(255)
                
            rect(mapSideSize + x * mapChipSize, mapSideSize + y * mapChipSize, mapChipSize, mapChipSize)

#テキストを表示
def DrawText(_str):
    stroke(0)
    line(0,textAreaY, width, textAreaY)
    textSize(20)
    textAlign(LEFT)
    fill(0)
    text(_str, 10, height - textAreaSizeY / 2 + 7)

def settings():
    size(mapSizeX * mapChipSize + mapSideSize * 2, mapSizeY * mapChipSize + mapSideSize * 2 + textAreaSizeY)

def setup():
    background(204,204,204)
    Init()
    MapInit(mapSizeX, mapSizeY)
    MapMake()
    global isAnimKabeEnd
    if(isAnimKabeEnd == True):
        Solve()
        MapDraw(mapData)
    if(isAnimSolveEnd == True):
        MapDraw(mapData)
    if(animMode == 0):
        DrawText("step:" + str(len(trueSolve.path)))
    
    
def draw():
    global isAnimKabeEnd
    global isAnimSolveEnd
    if(isAnimKabeEnd == False):
        global animKabe
        global animKabeNum
        
        if(animKabeNum >= len(animKabe)):
            isAnimKabeEnd = True
            Solve()
            delay(animNextDelay)
            return
        
        background(204,204,204)
        _pos = animKabe[animKabeNum]
        SetMapData(_pos.x, _pos.y, 1)
        animKabeNum += 1
        MapDraw(mapData)
        DrawText("KabeStep:" + str(animKabeNum) + " / " + str(len(animKabe)))
        delay(animKabeDelay)
    
    elif(isAnimSolveEnd == False):
        global animSolvestepNum
        global animSolveinStepNum
        
        if(animSolveMode == 1 and animSolveinStepNum >= len(solveHistory[animSolvestepNum])):
            animSolvestepNum += 1
            animSolveinStepNum = 0
        if(animSolvestepNum >= len(solveHistory)):
            global trueSolve
            isAnimSolveEnd = True
            for _pos in trueSolve.path:
                SetMapData(_pos.x, _pos.y, 6)
                MapDraw(mapData)
            return
        
        background(204,204,204)
        
        if(animSolveMode == 0):
            for _solve in solveHistory[animSolvestepNum]:
                for _pos in _solve.path:
                    SetMapData(_pos.x, _pos.y, 4)
            animSolvestepNum += 1
            DrawText("SolveStep:" + str(min(animSolvestepNum, len(solveHistory) - 1)) + " / " + str(len(solveHistory) - 1))
        elif(animSolveMode == 1):
            _solve = solveHistory[animSolvestepNum][animSolveinStepNum]
            for _pos in _solve.path:
                SetMapData(_pos.x, _pos.y, 4)
            animSolveinStepNum += 1
            DrawText("SolveStep:" + str(animSolvestepNum) + " / " + str(len(solveHistory) - 1) + "  inStep:" + str(animSolveinStepNum) + " / " + str(len(solveHistory[animSolvestepNum])))
        MapDraw(mapData)
        
        
        delay(animSolveDelay)
