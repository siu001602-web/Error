import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 웹 페이지 레이아웃 설정
st.set_page_config(
    page_title="디버깅 프로토콜 - 300 AI 서바이벌",
    page_icon="🤖",
    layout="wide"
)

st.title("⚡ 디버깅 프로토콜: 코드 서바이벌 (300 AI)")
st.caption("메모리 리소스를 독점하기 위한 300개 AI 개체의 실시간 시뮬레이션 시스템")

# --- 1. 초기 데이터 생성 및 세션 상태 초기화 ---
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
    st.session_state.logs = ["프로토콜 시작: 300개의 AI 프로세스가 메모리에 할당되었습니다."]
    st.session_state.running = False

# --- 2. 사이드바 컨트롤 패널 ---
st.sidebar.header("🕹️ 컨트롤 패널")

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("▶️ 실행 / 멈춤", use_container_width=True):
        st.session_state.running = not st.session_state.running

with col_btn2:
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("시뮬레이션 속도 (초)", 0.05, 1.0, 0.2)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**💡 기호 설명**
* 🔵 **정상 AI**: 연산 진행 중
* 🔴 **버그 AI**: 예외 발생으로 기능 저하
* ⬛ **가비지**: 메모리에서 삭제됨 (Garbage Collection)
""")

# --- 3. 핵심 서바이벌 로직 ---
def run_simulation_step():
    df = st.session_state.ais
    alive_df = df[df["alive"]]
    
    # 승리 조건 체크 (생존자 1 이하)
    if len(alive_df) <= 1:
        st.session_state.running = False
        if len(alive_df) == 1:
            winner = alive_df.iloc[0]['id']
            st.session_state.logs.insert(0, f"🏆 [SYSTEM] 승리: {winner} 가 모든 메모리를 독점했습니다!")
        return

    st.session_state.tick += 1
    logs = []
    
    # 매 틱마다 랜덤 상호작용 발생
    num_events = random.randint(5, 15)
    active_indices = alive_df.index.tolist()
    
    for _ in range(num_events):
        if len(active_indices) < 2:
            break
        
        idx1, idx2 = random.sample(active_indices, 2)
        ai1 = df.loc[idx1]
        ai2 = df.loc[idx2]

        event_type = random.choice(["attack", "attack", "bug", "patch"])

        if event_type == "attack":
            # 코드 흡수 공격
            damage = random.randint(20, 50)
            df.loc[idx2, "memory"] -= damage
            if df.loc[idx2, "memory"] <= 0:
                df.loc[idx2, "alive"] = False
                df.loc[idx1, "kills"] += 1
                df.loc[idx1, "memory"] = min(150, df.loc[idx1, "memory"] + 30)
                active_indices.remove(idx2)
                logs.append(f"💥 {ai1['id']} 가 {ai2['id']} 를 수집/파괴함 (Garbage Collection)")
            else:
                logs.append(f"⚔️ {ai1['id']} 가 {ai2['id']} 에 예외 공격 (-{damage}MB)")

        elif event_type == "bug":
            # 런타임 에러 전염
            df.loc[idx1, "status"] = "버그 래치"
            logs.append(f"⚠️ {ai1['id']} 에 런타임 예외(Runtime Error) 발생!")

        elif event_type == "patch":
            # 자가 리팩토링 및 치료
            df.loc[idx1, "memory"] = min(150, df.loc[idx1, "memory"] + 20)
            df.loc[idx1, "status"] = "정상"
            logs.append(f"🔧 {ai1['id']} 패치 실행 (메모리 회복)")

    st.session_state.logs = logs + st.session_state.logs[:40]

if st.session_state.running:
    run_simulation_step()

# --- 4. 대시보드 화면 구성 ---
alive_count = len(st.session_state.ais[st.session_state.ais["alive"]])
dead_count = TOTAL_AI - alive_count

m1, m2, m3, m4 = st.columns(4)
m1.metric("생존 AI 수", f"{alive_count} / {TOTAL_AI}", delta=f"-{dead_count}")
m2.metric("삭제된 가비지 (Garbage)", f"{dead_count}", delta_color="inverse")
m3.metric("진행 틱 (Tick)", f"{st.session_state.tick}")
m4.metric("시스템 연산 상태", "RUNNING" if st.session_state.running else "PAUSED")

st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🖥️ 300 AI 실시간 그리드 맵")
    
    df_chart = st.session_state.ais.copy()
    
    # 300개 AI를 15x20 좌표 매트릭스로 배치
    df_chart["x"] = np.repeat(range(20), 15)[:TOTAL_AI]
    df_chart["y"] = np.tile(range(15), 20)[:TOTAL_AI]
    
    # 상태 색상 및 사이즈 지정
    df_chart["display_color"] = df_chart.apply(
        lambda r: "#3B82F6" if r["alive"] and r["status"] == "정상" 
        else ("#EF4444" if r["alive"] and r["status"] == "버그 래치" else "#1E293B"), axis=1
    )
    df_chart["display_size"] = df_chart.apply(lambda r: max(r["memory"], 10) if r["alive"] else 5, axis=1)

    st.scatter_chart(
        df_chart,
        x="x",
        y="y",
        color="display_color",
        size="display_size",
        height=400
    )

with col_right:
    st.subheader("📜 시스템 디버그 로그")
    log_text = "\n".join(st.session_state.logs[:15])
    st.text_area("로그 터미널", log_text, height=360, disabled=True)

# 리더보드
st.subheader("🏆 메모리 독점 상위 생존 AI")
top_ais = st.session_state.ais[st.session_state.ais["alive"]].sort_values(by="kills", ascending=False).head(5)
st.dataframe(top_ais[["id", "type", "memory", "kills", "status"]], use_container_width=True)

# 자동 루프 리프레시
if st.session_state.running:
    time.sleep(speed)
    st.rerun()
