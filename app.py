import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(
    page_title="디지털 콜로세움 - 300 AI 서바이벌 대장정",
    page_icon="🏟️",
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
            "skill_type": skill["skill_type"] if "skill_type" in skill else skill["type"],
            "wins": 0,
            "losses": 0,
            "stage": 1, # 1: 1라운드(5승전), 2: 2라운드(조별), 3: 3라운드(운빨토너먼트), 4~7: 토너먼트, 8: 탈락, 9: 우승
            "group": -1,
            "rank": 0
        })
    return ais

if "game_db" not in st.session_state:
    st.session_state.game_db = generate_ais()
    st.session_state.current_stage = 1
    st.session_state.logs = ["🏟️ 300 AI 콜로세움 대장정이 개막했습니다! [1라운드: 5승 진출전]"]
    st.session_state.running = False
    # 2라운드 조별리그 상태 관리 (15개 조, 조당 10명)
    st.session_state.groups_initialized = False
    # 3라운드 상태 관리 (32명 남을 때까지 무작위 운빨 매치)
    st.session_state.stage3_match_count = 0
    # 토너먼트 상태 관리
    st.session_state.tournament_match = None
    st.session_state.champion = None

# --- 전투 시뮬레이션 함수 ---
def fight(ai1, ai2):
    s1 = ai1["atk"] + ai1["spd"] + random.randint(1, 25)
    s2 = ai2["atk"] + ai2["spd"] + random.randint(1, 25)
    if s1 >= s2:
        return ai1, ai2
    else:
        return ai2, ai1

# --- 단계별 로직 ---
def run_step():
    stage = st.session_state.current_stage
    db = st.session_state.game_db
    
    # [1라운드] 5승 진출전 (150명 확정될 때까지)
    if stage == 1:
        active = [a for a in db if a["stage"] == 1]
        qualified = [a for a in db if a["stage"] > 1 and a["rank"] == 0] # 이미 진출한 인원
        
        if len(qualified) >= 150:
            # 탈락자 하늘에서 우수수 떨어지는 연출
            for a in active:
                a["stage"] = 8 # 탈락
                a["rank"] = 151
            st.session_state.logs.insert(0, "✨ [1라운드 종료] 150명 진출 확정! 통과하지 못한 150명의 닉네임이 하늘에서 우수수수 떨어져 소멸합니다! 🌠")
            st.session_state.current_stage = 2
            st.session_state.running = False
            return
            
        if len(active) < 2:
            st.session_state.current_stage = 2
            return
            
        ai1, ai2 = random.sample(active, 2)
        winner, loser = fight(ai1, ai2)
        winner["wins"] += 1
        loser["losses"] += 1
        st.session_state.logs.insert(0, f"⚔️ [1R] `{ai1['name']}` vs `{ai2['name']}` ➡️ 승자: **`{winner['name']}`** ({winner['wins']}승)")
        
        if winner["wins"] >= 5 and winner["stage"] == 1:
            winner["stage"] = 2
            st.session_state.logs.insert(0, f"🎉 `{winner['name']}` 5승 달성으로 2라운드 진출 확정!")

    # [2라운드] 15개 조별리그 (조당 10명, 조별 5명 생존 = 총 75명)
    elif stage == 2:
        if not st.session_state.groups_initialized:
            # 1라운드 통과한 150명을 15개 조로 10명씩 배치
            passed = [a for a in db if a["stage"] == 2]
            random.shuffle(passed)
            for i, a in enumerate(passed):
                a["group"] = i // 10 # 0 ~ 14조
            st.session_state.groups_initialized = True
            st.session_state.logs.insert(0, "📦 [2라운드 시작] 150명이 15개 조(조당 10명)로 편성되었습니다. 조별로 따로 돌릴 수 있습니다!")
            st.session_state.running = False
            return

    # [3라운드] 운빨 토너먼트 (32명 남을 때까지 무작위 매치, 패배시 탈락)
    elif stage == 3:
        active = [a for a in db if a["stage"] == 3]
        if len(active) <= 32:
            st.session_state.logs.insert(0, f"🔥 [3라운드 종료] 32명이 생존하여 본격 토너먼트(16강)로 진입합니다!")
            st.session_state.current_stage = 4 # 16강으로 이동
            # 남은 32명 stage를 4로 변경
            for a in active:
                a["stage"] = 4
            st.session_state.running = False
            return
            
        ai1, ai2 = random.sample(active, 2)
        winner, loser = fight(ai1, ai2)
        loser["stage"] = 8 # 패배 즉시 탈락
        loser["rank"] = len(active)
        st.session_state.logs.insert(0, f"🎲 [3R 운빨매치] `{ai1['name']}` vs `{ai2['name']}` ➡️ 승자: `{winner['name']}` / 탈락: `{loser['name']}`")

    # [4~7라운드] 진짜 토너먼트 (16강 -> 8강 -> 4강 -> 결승)
    elif stage in [4, 5, 6, 7]:
        active = [a for a in db if a["stage"] == stage]
        if len(active) <= 1 and stage == 7:
            # 최종 우승자
            if active:
                st.session_state.champion = active[0]
                active[0]["rank"] = 1
                st.session_state.logs.insert(0, f"👑 [최종 우승] `{active[0]['name']}`이(가) 콜로세움의 최종 챔피언이 되었습니다!")
            st.session_state.running = False
            return
            
        if len(active) % 2 != 0:
            # 홀수일 경우 임의 1명 부전승
            lucky = active.pop()
            lucky["stage"] += 1
            st.session_state.logs.insert(0, f"🎯 `{lucky['name']}` 부전승으로 다음 토너먼트 진출!")
            return
            
        ai1, ai2 = active[0], active[1]
        winner, loser = fight(ai1, ai2)
        loser["stage"] = 8 # 탈락
        loser["rank"] = len(active) * 2
        winner["stage"] += 1 # 다음 라운드로 승급
        st.session_state.tournament_match = {"p1": ai1, "p2": ai2, "winner": winner}
        st.session_state.logs.insert(0, f"🏟️ [{stage}강 매치] 모든 눈앞에서 격돌! `{ai1['name']}` vs `{ai2['name']}` ➡️ 승자: **`{winner['name']}`**")
        
        # 라운드 전환 체크
        remaining_in_stage = [a for a in db if a["stage"] == stage]
        if len(remaining_in_stage) == 0:
            st.session_state.current_stage += 1

# --- UI 레이아웃 ---
st.title("🏟️ 디지털 콜로세움: 300 AI 서바이벌 대장정")
st.caption("1라운드(5승) ➡️ 2라운드(15개 조별리그) ➡️ 3라운드(운빨 매치 32명) ➡️ 16강~결승 토너먼트")

st.sidebar.header("🕹️ 컨트롤 패널")
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("▶️ 자동 진행", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.button("🔄 전체 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("진행 속도 (초)", 0.01, 0.3, 0.05)

# 현재 단계 표시
stage_names = {1: "1라운드 (5승 진출전)", 2: "2라운드 (15개 조별리그)", 3: "3라운드 (운빨 토너먼트)", 4: "16강 토너먼트", 5: "8강 토너먼트", 6: "4강 토너먼트", 7: "결승전", 8: "종료"}
st.info(f"📍 **현재 페이즈:** {stage_names.get(st.session_state.current_stage, '종료')}")

# 자동 진행 루프
if st.session_state.running and st.session_state.current_stage < 8:
    run_step()

# --- 탭 구성으로 각 라운드/기능 분리 ---
tab1, tab2, tab3, tab4 = st.tabs(["⚔️ 메인 아레나 & 로그", "📦 2라운드 조별리그 제어", "📊 랭킹 및 생존자 현황", "📜 룰 설명"])

with tab1:
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.subheader("🔥 실시간 경기 콜로세움")
        if st.session_state.current_stage == 2:
            st.warning("⚠️ 2라운드(조별리그)는 [📦 2라운드 조별리그 제어] 탭에서 조별로 각각 실행할 수 있습니다!")
        elif st.session_state.tournament_match:
            m = st.session_state.tournament_match
            st.success(f"관중들이 지켜보는 눈앞에서 대결 중!\n\n **`{m['p1']['name']}`** VS **`{m['p2']['name']}`** \n\n 🏆 승자: **`{m['winner']['name']}`**")
        else:
            st.write("자동 진행 버튼을 눌러 시뮬레이션을 시작하세요.")
            
        st.markdown("---")
        st.subheader("📜 실시간 중계 로그")
        log_text = "\n".join(st.session_state.logs[:25])
        st.text_area("로그", log_text, height=350, disabled=True)
        
    with col_r:
        st.subheader("🏆 최종 챔피언")
        if st.session_state.champion:
            st.balloons()
            st.success(f"관중 환호 속 우승자: **{st.session_state.champion['name']}** 🎉")
        else:
            st.info("아직 챔피언이 탄생하지 않았습니다.")

with tab2:
    st.subheader("📦 2라운드 조별리그 (15개 조, 각 10명)")
    st.caption("각 조별로 개별 버튼을 눌러 생존자 5명씩을 선발할 수 있습니다. (통과 못 한 인원은 탈락)")
    
    if st.session_state.current_stage >= 2:
        if not st.session_state.groups_initialized:
            if st.button("🚀 2라운드 조 배정 시작하기"):
                run_step()
                st.rerun()
        else:
            cols = st.columns(3)
            for g_idx in range(15):
                with cols[g_idx % 3]:
                    st.markdown(f"**[ {g_idx + 1} 조 ]**")
                    group_members = [a for a in st.session_state.game_db if a["group"] == g_idx]
                    active_members = [a for a in group_members if a["stage"] == 2]
                    st.text(f"생존: {len(active_members)} / 10명")
                    
                    if st.button(f"▶️ {g_idx+1}조 경기 돌리기", key=f"g_btn_{g_idx}"):
                        # 해당 조에서 5명만 남을 때까지 경기 진행
                        group_active = [a for a in group_members if a["stage"] == 2]
                        while len(group_active) > 5 and len(group_active) >= 2:
                            a1, a2 = random.sample(group_active, 2)
                            w, l = fight(a1, a2)
                            l["stage"] = 8 # 탈락
                            group_active = [a for a in group_members if a["stage"] == 2]
                        # 살아남은 5명 3라운드로 진격
                        for a in group_active:
                            a["stage"] = 3
                        st.session_state.logs.insert(0, f"📦 [2라운드 {g_idx+1}조 완료] 5명 생존 확정 및 3라운드 진출!")
                        st.rerun()
                    st.markdown("---")
                    
            # 2라운드 모두 완료되었는지 확인 후 3라운드로 자동 전환 버튼
            all_stage2 = [a for a in st.session_state.game_db if a["stage"] == 2]
            if len(all_stage2) == 0 and st.session_state.current_stage == 2:
                if st.button("✨ 2라운드 종료하고 3라운드(운빨 토너먼트)로 넘어가기"):
                    st.session_state.current_stage = 3
                    st.session_state.logs.insert(0, "🎲 [3라운드 시작] 총 75명이 남았습니다. 32명이 남을 때까지 무작위 운빨 매치 시작!")
                    st.rerun()
    else:
        st.warning("아직 1라운드가 진행 중입니다.")

with tab3:
    st.subheader("📊 전체 AI 랭킹 및 생존 현황")
    df = pd.DataFrame(st.session_state.game_db)
    
    # 상태 텍스트 변환
    def get_status(row):
        if row["stage"] == 8: return "❌ 탈락"
        elif row["stage"] == 9 or row["rank"] == 1: return "👑 우승"
        elif row["stage"] == 7: return "🔥 결승 진출"
        elif row["stage"] == 6: return "⚔️ 4강 진출"
        elif row["stage"] == 5: return "⚔️ 8강 진출"
        elif row["stage"] == 4: return "⚔️ 16강 진출"
        elif row["stage"] == 3: return "🎲 3라운드(운빨)"
        elif row["stage"] == 2: return "📦 2라운드(조별)"
        else: return "🏃 1라운드(5승전)"
        
    df["현재상태"] = df.apply(get_status, axis=1)
    
    # 정렬 (생존자 우선, 승수 우선)
    df_sorted = df.sort_values(by=["stage", "wins"], ascending=[False, False])
    st.dataframe(
        df_sorted[["name", "현재상태", "wins", "losses", "atk", "def", "spd", "skill"]],
        use_container_width=True,
        height=450
    )

with tab4:
    st.markdown("""
    ### 📋 서바이벌 규칙 안내
    1. **1라운드 (5승 진출전):** 300명이 무작위 매치를 거쳐 먼저 5승을 달성한 150명만 생존합니다. 탈락한 150명은 하늘에서 우수수 떨어집니다!
    2. **2라운드 (조별리그):** 통과한 150명이 15개 조(조당 10명)로 나뉘어 조별리그를 치릅니다. 각 조별로 따로 버튼을 눌러 5명씩(총 75명) 생존시킬 수 있습니다.
    3. **3라운드 (운빨 토너먼트):** 75명이 무작위 운빨 매치를 벌여 패배시 즉시 탈락합니다. **32명**이 남을 때까지 진행됩니다.
    4. **4~7라운드 (본격 토너먼트):** 16강(4라운드) ➡️ 8강(5라운드) ➡️ 4강(6라운드) ➡️ 결승(7라운드) 순으로 모든 관중이 지켜보는 가운데 1:1 토너먼트를 펼쳐 최종 1위를 가립니다.
    """)

# 자동 루프 리프레시
if st.session_state.running and st.session_state.current_stage < 8:
    time.sleep(speed)
    st.rerun()
