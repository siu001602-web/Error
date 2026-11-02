import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(
    page_title="디버깅 프로토콜 - 300 AI 서바이벌",
    page_icon="🤖",
    layout="wide"
)

st.title("⚡ 디버깅 프로토콜: 코드 서바이벌 (300 AI)")
st.caption("한정된 메모리 리소스를 차지하기 위한 300개 AI 개체의 실시간 시뮬레이션")

# --- 1. 초기화 설정 ---
TOTAL_AI = 300
TYPES = ["파서(Parser)", "컴파일러(Compiler)", "스캐너(Scanner)", "패처(Patcher)"]

if "ais" not in st.session_state:
    st.session_state.ais = pd.DataFrame({
        "id": [f"AI-{i+1:03d}" for i in range(TOTAL_AI)],
        "type": [random.choice(TYPES) for _ in range(TOTAL_AI)],
        "memory": np.random.randint(50, 100, size=TOTAL_AI),
        "status": ["정상" for _ in range(TOTAL_AI)],
        "kills": [0 for _ in range(TOTAL_AI)],
        "alive": [True for _ in range(TOTAL_AI)]
    })
    st.session_state.tick = 0
    st.session_state.logs = ["프로토콜 시작: 300개의 AI 프로세스가 할당되었습니다."]
    st.session_state.running = False

# --- 2. 사이드바 컨트롤 ---
st.sidebar.header("🕹️ 컨트롤 패널")

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("▶️ 실행 / 멈춤", use_container_width=True):
        st.session_state.running = not st.session_state.running

with col_btn2:
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("시뮬레이션 속도 (초)", 0.1, 1.0, 0.3)
st.sidebar.markdown("---")
st.sidebar.subheader("📊 시스템 리소스 정보")

# --- 3. 시뮬레이션 로직 ---
def run_simulation_step():
    df = st.session_state.ais
    alive_df = df[df["alive"]]
    
    if len(alive_df) <= 1:
        st.session_state.running = False
        if len(alive_df) == 1:
            winner = alive_df.iloc[0]['id']
            st.session_state.logs.insert(0, f"🏆 [SYSTEM] 최종 생존 완료: {winner}가 연산 자원을 완전히 독점했습니다!")
        return

    st.session_state.tick += 1
    logs = []
    
    # 300개 AI 중 무작위 상호작용 발생 (속도를 위해 샘플링)
    num_events = random.randint(5, 15)
    active_indices = alive_df.index.tolist()
    
    for _ in range(num_events):
        if len(active_indices) < 2:
            break
        
        idx1, idx2 = random.sample(active_indices, 2)
        ai1 = df.loc[idx1]
        ai2 = df.loc[idx2]

        event_type = random.choice(["attack", "bug", "patch"])

        if event_type == "attack":
            # AI 간 연산 공격
            damage = random.randint(15, 40)
            df.loc[idx2, "memory"] -= damage
            if df.loc[idx2, "memory"] <= 0:
                df.loc[idx2, "alive"] = False
                df.loc[idx1, "kills"] += 1
                df.loc[idx1, "memory"] = min(100, df.loc[idx1, "memory"] + 20) # 흡수
                active_indices.remove(idx2)
                logs.append(f"💥 {ai1['id']} 가 {ai2['id']} 를 파괴하고 코드를 흡수함 (가비지 컬렉션)")
            else:
                logs.append(f"⚔️ {ai1['id']} 가 {ai2['id']} 에게 메모리 공격 (-{damage}MB)")

        elif event_type == "bug":
            # 에러 감염
            df.loc[idx1, "status"] = "버그 래치"
            logs.append(f"⚠️ {ai1['id']} 에게 런타임 예외 버그 발생!")

        elif event_type == "patch":
            # 자가 패치
            df.loc[idx1, "memory"] = min(100, df.loc[idx1, "memory"] + 15)
            df.loc[idx1, "status"] = "정상"
            logs.append(f"🔧 {ai1['id']} 가 패치 코드를 적용하여 메모리 회복")

    # 상단에 최신 로그 추가
    st.session_state.logs = logs + st.session_state.logs[:30]

if st.session_state.running:
    run_simulation_step()

# --- 4. 메인 화면 레이아웃 ---
alive_count = len(st.session_state.ais[st.session_state.ais["alive"]])
dead_count = TOTAL_AI - alive_count

m1, m2, m3, m4 = st.columns(4)
m1.metric("생존 AI 수", f"{alive_count} / {TOTAL_AI}", delta=f"-{dead_count}")
m2.metric("삭제된 코드(Garbage)", f"{dead_count}", delta_color="inverse")
m3.metric("진행 틱(Tick)", f"{st.session_state.tick}")
m4.metric("시스템 상태", "OVERCLOCKING" if st.session_state.running else "IDLE")

st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🖥️ 생존 프로세스 맵 (300 AI)")
    
    # AI 300개의 상태를 컬러 시각화 (산점도 그래프)
    df_chart = st.session_state.ais.copy()
    
    # 300개를 15x20 그리드로 배치
    df_chart["x"] = np.repeat(range(20), 15)[:TOTAL_AI]
    df_chart["y"] = np.tile(range(15), 20)[:TOTAL_AI]
    
    # 상태별 색상 및 가시성 설정
    df_chart["display_color"] = df_chart.apply(
        lambda r: "#3B82F6" if r["alive"] and r["status"] == "정상" 
        else ("#EF4444" if r["alive"] and r["status"] == "버그 래치" else "#1F2937"), axis=1
    )
    df_chart["display_size"] = df_chart["memory"].apply(lambda m: max(m, 5))

    st.scatter_chart(
        df_chart,
        x="x",
        y="y",
        color="display_color",
        size="display_size",
        height=380
    )

    st.caption("🔵 정상 AI | 🔴 버그 감염 AI | ⬛ 삭제된 프로세스 (크기는 남은 메모리 량)")

with col_right:
    st.subheader("📜 실시간 시스템 로그")
    log_text = "\n".join(st.session_state.logs[:15])
    st.text_area("로그 뷰어", log_text, height=350, disabled=True)

# 킬 스코어 리더보드
st.subheader("🏆 메모리 독점 상위 AI")
top_ais = st.session_state.ais[st.session_state.ais["alive"]].sort_values(by="kills", ascending=False).head(5)
st.dataframe(top_ais[["id", "type", "memory", "kills", "status"]], use_container_width=True)

# 자동 새로고침 (실행 중일 때만)
if st.session_state.running:
    time.sleep(speed)
    st.rerun()
