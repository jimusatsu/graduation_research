import gurobipy as gp
from gurobipy import *
import numpy as np
import pandas as pd

def optimize_antenna_placement(n):
    # 定数の設定
    k = 11
    P_min = 1
    r_min = 0.75
    r_max = 7.5
    A_max = 30

    # 集合AとCの定義
    A = [(i % k, i // k) for i in range(k**2)]
    C = [(np.random.uniform(0, k-1), np.random.uniform(0, k-1)) for _ in range(n)]

    # Gurobiモデルの初期化
    model = gp.Model("antenna_optimization")

    # 変数の定義
    R = model.addVars(range(k**2), vtype=GRB.CONTINUOUS, lb=r_min**2, ub=r_max**2, name="R")
    X = model.addVars(range(k**2), vtype=GRB.BINARY, name="X")
    W = model.addVars(range(k**2), range(n), vtype=GRB.BINARY, name="W")

    # 目的関数の設定
    model.setObjective(gp.quicksum(P_min / (r_min**2) * R[i] * X[i] for i in range(k**2)), GRB.MINIMIZE)

    # 制約条件の設定
    for j in range(n):
        model.addConstr(gp.quicksum(X[i] * W[i, j] for i in range(k**2)) >= 1)

    model.addConstr(gp.quicksum(X[i] for i in range(k**2)) <= A_max)

    for i in range(k**2):
        for j in range(n):
            model.addGenConstrIndicator(W[i, j], True, ((A[i][0] - C[j][0])**2 + (A[i][1] - C[j][1])**2) <= R[i])

    # モデルの最適化
    model.optimize()

    # 結果の返却
    if model.status == GRB.OPTIMAL:
        return model.objVal
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
result_df.to_excel("optimization_result_variable.xlsx", index=False)
