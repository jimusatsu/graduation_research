import numpy as np
import pandas as pd

def cover_max_devices_greedy(n, k=11, r_min=0.75, A_max=30):
    # アンテナおよび端末の座標を生成
    A = [(i % k, i // k) for i in range(k**2)]
    C = [(np.random.uniform(0, k-1), np.random.uniform(0, k-1)) for _ in range(n)]

    # 各アンテナがカバーできる端末を記録
    coverage = {}
    for i in range(k**2):
        coverage[i] = {j for j, c in enumerate(C) if (A[i][0] - c[0])**2 + (A[i][1] - c[1])**2 <= r_min**2}

    # 使用するアンテナを選択
    selected_antennas = set()
    covered_devices = set()
    while len(selected_antennas) < A_max and len(covered_devices) < n:
        # 未カバーの端末を最も多くカバーできるアンテナを選択
        best_antenna = None
        best_coverage = 0
        for i, devs in coverage.items():
            current_coverage = len(devs - covered_devices)
            if current_coverage > best_coverage:
                best_antenna = i
                best_coverage = current_coverage

        # 選択したアンテナを追加
        if best_antenna is not None:
            selected_antennas.add(best_antenna)
            covered_devices.update(coverage[best_antenna])

    # カバーされなかった端末の数を計算
    uncovered_devices = n - len(covered_devices)
    return uncovered_devices

# 結果を格納するためのデータフレームを作成
result_df = pd.DataFrame(columns=["端末数n", "平均ブロック率"])

for n in range(1, 101):
    values = []
    # 各端末数ごとに20回異なるseed値を生成
    for i in range(20):
        seed_value = hash((n, i)) % (2**32)  # hash関数を使用してseed_valueを生成
        np.random.seed(seed_value)

        result = cover_max_devices_greedy(n)
        values.append(result)

    average_value = np.mean(values)
    block_percent = average_value / n * 100

    # 結果をデータフレームに追加
    new_row = pd.DataFrame([[n, block_percent]], columns=result_df.columns)
    result_df = pd.concat([result_df, new_row], ignore_index=True)


# 結果をエクセルファイルに書き出す
result_df.to_excel("optimization_result_mini_block.xlsx", index=False)
