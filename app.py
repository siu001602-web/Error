import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(
    page_title="디버깅 프로토콜 - 아레나 맵",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 디버깅 프로토콜: 2D 아레나 서바이벌 (300 AI)")
st.caption("300개의 AI 프로세스가 가상 아레나 지도에서 메모리를 두고 격돌하는 실시간 맵")

# --- 1. 초기 데이터 설정 (2D 좌표 x, y 추가) ---
TOTAL_AI = 300
TYPES = ["파서(Parser)", "컴파일러(Compiler)", "스캐너(Scanner)", "패처(Patcher)"]

if "ais" not in st.session_state:
    st.session_state.ais = pd.DataFrame({
        "id": [f"AI-{i+1:03d}" for i in range(TOTAL_AI)],
        "type": [random.choice(TYPES) for _ in range(TOTAL_AI)],
        "x": np.random.uniform(0, 100, size=TOTAL_AI),
        "y": np.random.uniform(0, 100, size=TOTAL_AI),
        "memory": np.random.randint(50, 100, size=TOTAL_AI),
        "status": ["정상" for _ in range(TOTAL_AI)],
        "kills": [0 for _ in range(TOTAL_AI)],
        "alive": [True for _ in range(TOTAL_AI)]
    })
    st.session_state.tick = 0
    st.session_state.logs = ["아레나 초기화 완료: 300개 프로세스 배치됨."]
    st.session_state.running = False

# --- 2. 컨트롤 패널 ---
st.sidebar.header("🕹️ 아레나 컨트롤")
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("▶️ 실행 / 멈춤", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("시뮬레이션 속도 (초)", 0.05, 1.0, 0.2)

# --- 3. 시뮬레이션 및 이동 로직 ---
def run_simulation_step():
    df = st.session_state.ais
    alive_indices = df[df["alive"]].index.tolist()
    
    if len(alive_indices) <= 1:
        st.session_state.running = False
        if len(alive_indices) == 1:
            winner = df.loc[alive_indices[0], 'id']
            st.session_state.logs.insert(0, f"🏆 [아레나 종료] 최종 승자: {winner}")
        return

    st.session_state.tick += 1
    logs = []

    # 1) 모든 살아있는 AI가 무작위 방향으로 한 칸씩 이동 (지도 위를 돌아다님)
    for idx in alive_indices:
        dx = random.uniform(-3, 3)
        dy = random.uniform(-3, 3)
        df.loc[idx, "x"] = np.clip(df.loc[idx, "x"] + dx, 0, 100)
        df.loc[idx, "y"] = np.clip(df.loc[idx, "y"] + dy, 0, 100)

    # 2) 상호작용 (전투, 버그, 패치)
    num_events = random.randint(5, 12)
    for _ in range(num_events):
        if len(alive_indices) < 2:
            break
        idx1, idx2 = random.sample(alive_indices, 2)
        ai1, ai2 = df.loc[idx1], df.loc[idx2]

        event_type = random.choice(["attack", "attack", "bug", "patch"])

        if event_type == "attack":
            damage = random.randint(20, 45)
            df.loc[idx2, "memory"] -= damage
            if df.loc[idx2, "memory"] <= 0:
                df.loc[idx2, "alive"] = False
                df.loc[idx1, "kills"] += 1
                df.loc[idx1, "memory"] = min(150, df.loc[idx1, "memory"] + 30)
                alive_indices.remove(idx2)
                logs.append(f"💥 [{ai1['id']}]가 [{ai2['id']}]를 소멸시킴 (Garbage Collection)")
            else:
                logs.append(f"⚔️ [{ai1['id']}] ➡️ [{ai2['id']}] 공격 (-{damage}MB)")
        elif event_type == "bug":
            df.loc[idx1, "status"] = "버그 감염"
            logs.append(f"⚠️ [{ai1['id']}] 버그 발생!")
        elif event_type == "patch":
            df.loc[idx1, "memory"] = min(150, df.loc[idx1, "memory"] + 20)
            df.loc[idx1, "status"] = "정상"
            logs.append(f"🔧 [{ai1['id']}] 패치 완료")

    st.session_state.logs = logs + st.session_state.logs[:40]

if st.session_state.running:
    run_simulation_step()

# --- 4. 화면 레이아웃 (지도 중심) ---
alive_count = len(st.session_state.ais[st.session_state.ais["alive"]])
dead_count = TOTAL_AI - alive_count

m1, m2, m3, m4 = st.columns(4)
m1.metric("생존 프로세스", f"{alive_count}개")
m2.metric("삭제된 가비지", f"{dead_count}개", delta_color="inverse")
m3.metric("아레나 틱", f"{st.session_state.tick}")
m4.metric("시뮬레이션 상태", "전투 중 🔥" if st.session_state.running else "대기 중 ⏸️")

st.markdown("---")

col_map, col_log = st.columns([2, 1])

with col_map:
    st.subheader("🌐 실시간 아레나 맵 (0~100 좌표계)")
    
    df_chart = st.session_state.ais.copy()
    
    # 색상 지정 (정상: 파랑, 버그: 빨강, 사망: 회색)
    df_chart["color"] = df_chart.apply(
        lambda r: "#3B82F6" if r["alive"] and r["status"] == "정상" 
        else ("#EF4444" if r["alive"] and r["status"] == "버그 감염" else "#334155"), axis=1
    )
    df_chart["size"] = df_chart.apply(lambda r: max(r["memory"], 10) if r["alive"] else 5, axis=1)

    # 산점도를 지도처럼 활용 (0~100 범위 고정)
    st.scatter_chart(
        df_chart,
        x="x",
        y="y",
        color="color",
        size="size",
        height=450
    )
    st.caption("파란색 점: 정상 AI | 빨간색 점: 버그 걸린 AI | 어두운 점: 소멸된 AI (점 크기 = 남은 메모리)")

with col_log:
    st.subheader("📜 실시간 전투 로그")
    log_text = "\n".join(st.session_state.logs[:18])
    st.text_area("로그", log_text, height=430, disabled=True)

# 하단 리더보드
st.subheader("🏆 메모리 랭킹 상위권")
top_ais = st.session_state.ais[st.session_state.ais["alive"]].sort_values(by="kills", ascending=False).head(5)
st.dataframe(top_ais[["id", "type", "x", "y", "memory", "kills", "status"]], use_container_width=True)

if st.session_state.running:
    time.sleep(speed)
    st.rerun()
