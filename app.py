import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(
    page_title="디지털 콜로세움 - 300 AI 토너먼트",
    page_icon="⚔️",
    layout="wide"
)

# --- 닉네임 generator 요소 ---
PREFIXES = ["네온", "사이보그", "스펙터", "바이퍼", "알파", "오메가", "섀도우", "퀀텀", "하이퍼", "타이탄", "보이드", "제니스", "크로노스", "아크", "맥스", "고스트", "블레이드", "세이버"]
NAMES = ["헌터", "프로토콜", "스캐너", "컴파일러", "파서", "가디언", "스트라이커", "위버", "코어", "소울", "엔진", "노드", "벡터", "셀", "센티널", "블래스터"]
SKILLS = [
    {"name": "오버클럭 (공격력 +50%)", "type": "buff_atk"},
    {"name": "방화벽 뚫기 (방어 무시)", "type": "pierce"},
    {"name": "회피 알고리즘 (공격 회피)", "type": "dodge"},
    {"name": "메모리 흡수 (피해량 회복)", "type": "heal"},
    {"name": "치명적 버그 (2배 데미지)", "type": "crit"}
]

# --- 1. AI 300명 생성 및 데이터 초기화 ---
TOTAL_AI = 300

def generate_ais():
    ais = []
    used_names = set()
    
    for i in range(1, TOTAL_AI + 1):
        # 중복 없는 닉네임 생성
        while True:
            nickname = f"{random.choice(PREFIXES)}_{random.choice(NAMES)}-{random.randint(10, 99)}"
            if nickname not in used_names:
                used_names.add(nickname)
                break
                
        skill = random.choice(SKILLS)
        ais.append({
            "id": f"AI-{i:03d}",
            "name": nickname,
            "hp": 100,
            "max_hp": 100,
            "atk": random.randint(15, 35),
            "def": random.randint(5, 20),
            "spd": random.randint(10, 30),
            "skill": skill["name"],
            "skill_type": skill["type"],
            "wins": 0,
            "alive": True
        })
    return ais

if "ais_db" not in st.session_state:
    st.session_state.ais_db = generate_ais()
    st.session_state.current_round_players = st.session_state.ais_db.copy()
    st.session_state.next_round_players = []
    st.session_state.round_num = 1
    st.session_state.match_logs = ["🏛️ 디지털 콜로세움 300 AI 토너먼트가 개막했습니다!"]
    st.session_state.running = False
    st.session_state.champion = None
    st.session_state.current_match = None

# --- 2. 대결(1:1) 로직 ---
def simulate_match(ai1, ai2):
    logs = [f"⚔️ **[매치]** `{ai1['name']}` vs `{ai2['name']}` 대결 시작!"]
    
    hp1, hp2 = ai1['hp'], ai2['hp']
    
    # 민첩성(spd)에 따른 선공 결정
    turn = 0 if ai1['spd'] >= ai2['spd'] else 1
    
    rounds = 0
    while hp1 > 0 and hp2 > 0 and rounds < 20:
        rounds += 1
        attacker = ai1 if turn == 0 else ai2
        defender = ai2 if turn == 0 else ai1
        
        # 회피 체크
        if defender['skill_type'] == "dodge" and random.random() < 0.3:
            logs.append(f"🌀 `{defender['name']}`이(가) 스킬 [{defender['skill']}] 발동! 공격을 회피했습니다.")
            turn = 1 - turn
            continue
            
        # 데미지 계산
        atk_power = attacker['atk']
        if attacker['skill_type'] == "buff_atk" and random.random() < 0.4:
            atk_power = int(atk_power * 1.5)
            logs.append(f"🔥 `{attacker['name']}`의 [{attacker['skill']}] 발동! (공격력 증가)")
        elif attacker['skill_type'] == "crit" and random.random() < 0.3:
            atk_power = int(atk_power * 2.0)
            logs.append(f"💥 `{attacker['name']}`의 [{attacker['skill']}] 크리티컬!")
            
        def_power = defender['def'] if attacker['skill_type'] != "pierce" else 0
        if attacker['skill_type'] == "pierce":
            logs.append(f"🗡️ `{attacker['name']}`의 [{attacker['skill']}]! 방어력을 무시합니다.")
            
        damage = max(5, atk_power - def_power + random.randint(-3, 5))
        
        if turn == 0:
            hp2 -= damage
            if attacker['skill_type'] == "heal" and random.random() < 0.3:
                heal = int(damage * 0.5)
                hp1 = min(ai1['max_hp'], hp1 + heal)
                logs.append(f"💚 `{attacker['name']}`이(가) {heal} HP를 회복했습니다.")
        else:
            hp1 -= damage
            if attacker['skill_type'] == "heal" and random.random() < 0.3:
                heal = int(damage * 0.5)
                hp2 = min(ai2['max_hp'], hp2 + heal)
                logs.append(f"💚 `{attacker['name']}`이(가) {heal} HP를 회복했습니다.")
                
        turn = 1 - turn

    if hp1 > hp2:
        winner, loser = ai1, ai2
    else:
        winner, loser = ai2, ai1
        
    winner['wins'] += 1
    winner['hp'] = winner['max_hp'] # 다음 라운드를 위해 체력 회복
    loser['alive'] = False
    
    logs.append(f"🏆 **승자:** `{winner['name']}` (잔여 HP: {max(0, max(hp1, hp2))})")
    return winner, loser, logs

# --- 3. 토너먼트 진행 로직 ---
def step_tournament():
    players = st.session_state.current_round_players
    
    if len(players) == 1:
        st.session_state.champion = players[0]
        st.session_state.running = False
        st.session_state.match_logs.insert(0, f"👑 **[최종 챔피언]** `{players[0]['name']}`이(가) 300개의 AI를 제치고 콜로세움의 왕좌에 올랐습니다!")
        return

    # 대결 짝짓기
    if len(players) % 2 != 0:
        # 홀수명일 경우 1명 부전승
        bye_player = players.pop(random.randint(0, len(players) - 1))
        st.session_state.next_round_players.append(bye_player)
        st.session_state.match_logs.insert(0, f"🎯 `{bye_player['name']}`이(가) 부전승으로 다음 라운드 진출!")

    p1 = players.pop(0)
    p2 = players.pop(0)
    
    winner, loser, logs = simulate_match(p1, p2)
    st.session_state.next_round_players.append(winner)
    st.session_state.current_match = {"p1": p1, "p2": p2, "winner": winner, "logs": logs}
    
    for l in reversed(logs):
        st.session_state.match_logs.insert(0, l)
        
    # 라운드 종료 체크
    if len(players) == 0:
        st.session_state.current_round_players = st.session_state.next_round_players.copy()
        st.session_state.next_round_players = []
        st.session_state.round_num += 1
        st.session_state.match_logs.insert(0, f"🔔 **--- 라운드 {st.session_state.round_num} 시작 (남은 AI: {len(st.session_state.current_round_players)}명) ---**")

# --- 4. UI 레이아웃 및 컨트롤 ---
st.title("🏛️ 디지털 콜로세움: 300 AI 토너먼트")
st.caption("300개의 독자적인 AI가 능력치와 스킬로 맞붙는 대규모 토너먼트 배틀 아레나")

st.sidebar.header("🕹️ 콜로세움 제어")
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("▶️ 토너먼트 진행", use_container_width=True):
        st.session_state.running = not st.session_state.running
with col_b2:
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.clear()
        st.rerun()

speed = st.sidebar.slider("경기 진행 속도 (초)", 0.01, 0.5, 0.1)

# 메인 지표 표시
col1, col2, col3, col4 = st.columns(4)
alive_ais = [a for a in st.session_state.ais_db if a['alive']]
col1.metric("🏆 남은 생존 AI", f"{len(alive_ais)} / {TOTAL_AI} 명")
col2.metric("🥊 현재 라운드", f"Round {st.session_state.round_num}")
col3.metric("남은 대진 수", f"{len(st.session_state.current_round_players) // 2} 경기")
col4.metric("챔피언 상태", st.session_state.champion['name'] if st.session_state.champion else "경쟁 중 🔥")

st.markdown("---")

# 진행 중 로직
if st.session_state.running and not st.session_state.champion:
    step_tournament()

# 레이아웃 분할: 좌(현재 매치 / 참가자 정보), 우(전투 로그)
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("⚔️ 실시간 매치 아레나")
    if st.session_state.current_match:
        m = st.session_state.current_match
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**{m['p1']['name']}**\n\n"
                    f"⚔️ ATK: {m['p1']['atk']} | 🛡️ DEF: {m['p1']['def']} | ⚡ SPD: {m['p1']['spd']}\n\n"
                    f"🔮 스킬: `{m['p1']['skill']}`\n\n"
                    f"🏆 누적 승수: {m['p1']['wins']}승")
        with c2:
            st.warning(f"**{m['p2']['name']}**\n\n"
                       f"⚔️ ATK: {m['p2']['atk']} | 🛡️ DEF: {m['p2']['def']} | ⚡ SPD: {m['p2']['spd']}\n\n"
                       f"🔮 스킬: `{m['p2']['skill']}`\n\n"
                       f"🏆 누적 승수: {m['p2']['wins']}승")
    else:
        st.write("진행 버튼을 눌러 경기를 시작하세요.")

    st.subheader("📊 300 AI 대진 스펙 (상위 승수)")
    df_ais = pd.DataFrame(st.session_state.ais_db)
    df_sorted = df_ais.sort_values(by=["alive", "wins", "atk"], ascending=[False, False, False])
    st.dataframe(
        df_sorted[["name", "alive", "wins", "atk", "def", "spd", "skill"]],
        use_container_width=True,
        height=300
    )

with col_right:
    st.subheader("📜 콜로세움 중계 로그")
    log_text = "\n".join(st.session_state.match_logs[:25])
    st.text_area("중계창", log_text, height=480, disabled=True)

# 자동 리프레시 루프
if st.session_state.running and not st.session_state.champion:
    time.sleep(speed)
    st.rerun()
