import gurobipy as gp
from gurobipy import *
import numpy as np
import pandas as pd

def optimize_antenna_placement(n):
    # 定数
    k = 11
    P_min = 1
    r_max = 7.5
    A_max = 30

    # アンテナおよび端末の座標を生成
    A = [(i % k, i // k) for i in range(k**2)]
    C = [(np.random.uniform(0, k-1), np.random.uniform(0, k-1)) for _ in range(n)]

    # Gurobiモデルの作成
    model = gp.Model("antenna_placement")

    # 変数の作成
    X = {i: model.addVar(vtype=GRB.BINARY, name=f"X_{i}") for i in range(k**2)}
    W = {(i, j): model.addVar(vtype=GRB.BINARY, name=f"W_{i}_{j}") for i in range(k**2) for j in range(n)}

    # 目的関数の設定
    objective = 100 * P_min * gp.quicksum(X[i] for i in range(k**2))
    model.setObjective(objective, GRB.MINIMIZE)

    # 制約条件の設定
    # 全端末が稼働しているアンテナのセルに含まれる条件
    for j in range(n):
        model.addConstr(gp.quicksum(X[i] * W[i, j] for i in range(k**2)) >= 1)
    
    # アンテナの同時稼働数制限
    model.addConstr(gp.quicksum(X[i] for i in range(k**2)) <= A_max)

    # 0-1変数W_{ij}を定義する不等式
    for i in range(k**2):
        for j in range(n):
            distance = (A[i][0] - C[j][0])**2 + (A[i][1] - C[j][1])**2
            model.addConstr(W[i, j] == (distance <= r_max**2))

    # 最適化の実行
    model.optimize()

    # 結果の出力
    if model.status == GRB.OPTIMAL:
        return model.ObjVal
    else:
        return None

# 結果を格納するためのデータフレームを作成
result_df = pd.DataFrame(columns=["端末数n", "出力合計値の平均[P_min]"])

for n in range(1, 101):
    obj_values = []
    # 各端末数ごとに20回異なるseed値を生成
    for i in range(20):
        seed_value = hash((n, i)) % (2**32)  # hash関数を使用してseed_valueを生成
        np.random.seed(seed_value)

        result = optimize_antenna_placement(n)
        if result is not None:
            obj_values.append(result)

    if obj_values:
        average_obj_value = np.mean(obj_values)
    else:
        average_obj_value = '-'

    # 結果をデータフレームに追加
    new_row = pd.DataFrame([[n, average_obj_value]], columns=result_df.columns)
    result_df = pd.concat([result_df, new_row], ignore_index=True)


# 結果をエクセルファイルに書き出す
result_df.to_excel("optimization_result_maximum.xlsx", index=False)
