import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(
    page_title="디지털 콜로세움 - 5승 진출전",
    page_icon="⚔️",
    layout="wide"
)

# 닉네임 생성용 프리픽스 및 네임
PREFIXES = ["네온", "사이보그", "스펙터", "바이퍼", "알파", "오메가", "섀도우", "퀀텀", "하이퍼", "타이탄", "보이드", "제니스", "크로노스", "아크", "맥스", "고스트", "블레이드", "세이버"]
NAMES = ["헌터", "프로토콜", "스캐너", "컴파일러", "파서", "가디언", "스트라이커", "위버", "코어", "소울", "엔진", "노드", "벡터", "셀", "센티널", "블래스터"]
SKILLS = [
    {"name": "오버클럭 (공격력 +50%)", "type": "buff_atk"},
    {"name": "방화벽 뚫기 (방어 무시)", "type": "pierce"},
    {"name": "회피 알고리즘 (공격 회피)", "type": "dodge"},
    {"name": "메모리 흡수 (피해량 회복)", "type": "heal"},
    {"name": "치명적 버그 (2배 데미지)", "type": "crit"}
]

TOTAL_AI = 300
TARGET_WINS = 5  # 진출에 필요한 승수
TARGET_SURVIVORS = 150 # 진출 인원

def generate_ais():
    ais = []
    used_names = set()
    for i in range(1, TOTAL_AI + 1):
        while True:
            nickname = f"{random.choice(PREFIXES)}_{random.choice(NAMES)}-{random.randint(10, 99)}"
            if nickname not in used_names:
                used_names.add(nickname)
                break
        skill = random.choice(SKILLS)
        ais.append({
            "id": f"AI-{i:03d}",
            "name": nickname,
            "atk": random.randint(15, 35),
            "def": random.randint(5, 20),
            "spd": random.randint(10, 30),
            "skill": skill["name"],
            "skill_type": skill["type"],
            "wins": 0,
            "losses": 0,
            "status": "생존 (리그전 중)"
        })
    return ais

if "league_db" not in st.session_state:
    st.session_state.league_db = generate_ais()
    st.session_state.round_num = 1
    st.session_state.league_logs = ["🏛️ 300 AI 5승 진출 리그전이 시작되었습니다! (목표: 5승 달성)"]
    st.session_state.running = False
    st.session_state.qualified_count = 0

# --- 리그전 매치 시뮬레이션 로직 ---
def simulate_league_step():
    db = st.session_state.league_db
    # 아직 진출하지 않고 생존 중인 AI들 필터링
    active_ais = [ai for ai in db if ai["status"] == "생존 (리그전 중)"]
    
    if len(active_ais) < 2:
        st.session_state.running = False
        st.session_state.league_logs.insert(0, "🏆 모든 라운드 진출자가 확정되었습니다!")
        return

    # 무작위로 2명을 뽑아 매치 진행
    ai1, ai2 = random.sample(active_ais, 2)
    
    # 간단한 전투 판정 (능력치 + 랜덤성)
    score1 = ai1["atk"] + ai1["spd"] + random.randint(1, 20)
    score2 = ai2["atk"] + ai2["spd"] + random.randint(1, 20)
    
    if score1 >= score2:
        winner, loser = ai1, ai2
    else:
        winner, loser = ai2, ai1
        
    winner["wins"] += 1
    loser["losses"] += 1
    
    st.session_state.league_logs.insert(0, f"⚔️ `{ai1['name']}` vs `{ai2['name']}` ➡️ 승자: **`{winner['name']}`** (현재 {winner['wins']}승)")
    
    # 5승 달성 체크
    if winner["wins"] >= TARGET_WINS and winner["status"] == "생존 (리그전 중)":
        winner["status"] = "✨ 라운드 진출 확정!"
        st.session_state.qualified_count += 1
        st.session_state.league_logs.insert(0, f"🎉 **[{winner['name']}]**이(가) 5승을 달성하여 다음 라운드 진출 확정! ({st.session_state.qualified_count}/{TARGET_SURVIVORS}명)")
        
        # 150명이 모두 진출하면 종료
        if st.session_state.qualified_count >= TARGET_SURVIVORS:
            st.session_state.running = False
            st.session_state.league_logs.insert(0, f"🏁 **목표 진출자 {TARGET_SURVIVORS}명 달성 완료!** 리그전이 종료되었습니다.")

# --- UI 레이아웃 ---
st.title("🏛️ 디지털 콜로세움: 5승 진출 리그전 (300 AI)")
st.caption("300개의 AI가 무작위로 매치업을 가져, 먼저 5승을 달성하는 상위 150명만 다음 라운드로 진출합니다!")

st.sidebar.header("🕹️ 리그 컨트롤")
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("▶️ 리그전 진행", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("진행 속도 (초)", 0.01, 0.3, 0.05)

# 상단 메트릭
m1, m2, m3, m4 = st.columns(4)
m1.metric("총 참가 AI", f"{TOTAL_AI}명")
m2.metric("진출 확정된 AI", f"{st.session_state.qualified_count} / {TARGET_SURVIVORS}명")
m3.metric("진출 목표 승수", f"{TARGET_WINS}승")
m4.metric("리그 상태", "진행 중 🔥" if st.session_state.running else "정지 ⏸️")

st.markdown("---")

if st.session_state.running and st.session_state.qualified_count < TARGET_SURVIVORS:
    simulate_league_step()

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 전체 AI 리그 현황 (승수 순)")
    df_league = pd.DataFrame(st.session_state.league_db)
    df_sorted = df_league.sort_values(by=["wins", "losses", "atk"], ascending=[False, True, False])
    st.dataframe(
        df_sorted[["name", "status", "wins", "losses", "atk", "def", "spd", "skill"]],
        use_container_width=True,
        height=400
    )

with col_right:
    st.subheader("📜 실시간 리그 중계 로그")
    log_text = "\n".join(st.session_state.league_logs[:30])
    st.text_area("중계창", log_text, height=400, disabled=True)

if st.session_state.running and st.session_state.qualified_count < TARGET_SURVIVORS:
    time.sleep(speed)
    st.rerun()
