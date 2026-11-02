import random
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="좀비 웨이브 수비대", page_icon="🧟", layout="centered")

# --- 게임 상태 초기화 함수 ---
def init_game():
    st.session_state.player_hp = 100
    st.session_state.ap = 3          # 턴당 행동력
    st.session_state.wave = 1
    st.session_state.zombie_hp = 50
    st.session_state.zombie_max_hp = 50
    st.session_state.zombie_dist = 10  # 미터 단위 거리
    st.session_state.log = ["🧟 좀비들이 멀리서 다가오고 있습니다! 준비하세요!"]
    st.session_state.game_over = False

if "player_hp" not in st.session_state:
    init_game()

# --- 게임 로직 함수 ---
def next_turn_zombie_action():
    """턴 종료 시 좀비의 이동 및 공격 처리"""
    if st.session_state.zombie_hp <= 0:
        return

    # 좀비 이동 (3~5m 접근)
    move = random.randint(3, 5)
    st.session_state.zombie_dist = max(0, st.session_state.zombie_dist - move)
    st.session_state.log.append(f"🏃 좀비가 {move}m 다가왔습니다! (현재 거리: {st.session_state.zombie_dist}m)")

    # 좀비가 0m에 도달하면 플레이어 공격
    if st.session_state.zombie_dist == 0:
        damage = random.randint(15, 25)
        st.session_state.player_hp -= damage
        st.session_state.log.append(f"💥 좀비의 공격! 플레이어가 {damage} 피해를 입었습니다!")
        
        if st.session_state.player_hp <= 0:
            st.session_state.player_hp = 0
            st.session_state.game_over = True
            st.session_state.log.append("☠️ 플레이어가 패배했습니다... 게임 오버!")

def check_zombie_defeat():
    """좀비 처치 체크 및 다음 웨이브 진행"""
    if st.session_state.zombie_hp <= 0:
        st.session_state.wave += 1
        st.session_state.zombie_max_hp += 25
        st.session_state.zombie_hp = st.session_state.zombie_max_hp
        st.session_state.zombie_dist = 10 + random.randint(0, 3)
        st.session_state.ap = 3
        st.session_state.log.append(f"🎉 웨이브 클리어! [웨이브 {st.session_state.wave}] 더 강력한 좀비가 나타났습니다!")

# --- UI 레이아웃 ---
st.title("🧟 좀비 웨이브 수비대")
st.caption("카드(행동)를 선택하여 몰려오는 좀비를 막아내세요!")

# 다시 시작 버튼
if st.button("🔄 게임 리셋"):
    init_game()
    st.rerun()

st.divider()

# 1. 상단 상태바 (Metric)
col1, col2, col3, col4 = st.columns(4)
col1.metric("현재 웨이브", f"Wave {st.session_state.wave}")
col2.metric("내 체력 (HP)", f"{st.session_state.player_hp} / 100")
col3.metric("남은 행동력 (AP)", f"{st.session_state.ap} / 3")
col4.metric("좀비 거리", f"{st.session_state.zombie_dist} m")

# 좀비 체력 바
zombie_hp_ratio = max(0.0, st.session_state.zombie_hp / st.session_state.zombie_max_hp)
st.subheader(f"🧟 좀비 HP: {st.session_state.zombie_hp} / {st.session_state.zombie_max_hp}")
st.progress(zombie_hp_ratio)

st.divider()

# 2. 카드/행동 버튼 영역
st.subheader("🃏 행동 선택")

if not st.session_state.game_over:
    c1, c2, c3, c4 = st.columns(4)
    
    # 카드 1: 권총 사격 (비용 1)
    with c1:
        if st.button("🔫 권총 사격\n(소모: AP 1)", use_container_width=True, disabled=st.session_state.ap < 1):
            dmg = random.randint(10, 18)
            st.session_state.zombie_hp -= dmg
            st.session_state.ap -= 1
            st.session_state.log.append(f"🎯 권총 사격! 좀비에게 {dmg} 피해를 주었습니다.")
            check_zombie_defeat()
            st.rerun()

    # 카드 2: 샷건 발사 (비용 2)
    with c2:
        if st.button("💥 샷건 발사\n(소모: AP 2)", use_container_width=True, disabled=st.session_state.ap < 2):
            # 거리가 가까울수록 데미지 증가
            bonus = max(0, (10 - st.session_state.zombie_dist) * 2)
            dmg = random.randint(25, 35) + bonus
            st.session_state.zombie_hp -= dmg
            st.session_state.ap -= 2
            st.session_state.log.append(f"💥 샷건 발사! 좀비에게 {dmg} 강한 피해를 주었습니다!")
            check_zombie_defeat()
            st.rerun()

    # 카드 3: 밀쳐내기 (비용 1)
    with c3:
        if st.button("🛡️ 밀쳐내기\n(소모: AP 1)", use_container_width=True, disabled=st.session_state.ap < 1):
            push_dist = random.randint(3, 5)
            st.session_state.zombie_dist += push_dist
            st.session_state.ap -= 1
            st.session_state.log.append(f"🛡️ 좀비를 밀쳐내어 거리를 {push_dist}m 벌렸습니다!")
            st.rerun()

    # 턴 종료 버튼
    with c4:
        if st.button("⏭️ 턴 종료", use_container_width=True, type="primary"):
            st.session_state.log.append("--- 턴을 종료했습니다 ---")
            next_turn_zombie_action()
            st.session_state.ap = 3  # AP 회복
            st.rerun()

else:
    st.error("💀 게임 오버! 아래 리셋 버튼을 눌러 다시 도전하세요.")

st.divider()

# 3. 전투 로그 출력
st.subheader("📜 전투 기록")
log_box = "\n".join(reversed(st.session_state.log[-8:])) # 최근 8개 로그 출력
st.text_area("전투 로그", value=log_box, height=180, disabled=True)
