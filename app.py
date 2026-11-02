import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쉘터 30일 생존기", page_icon="🏕️", layout="centered")

# --- 게임 상태 초기화 ---
def init_game():
    st.session_state.day = 1
    st.session_state.hp = 100         # 내 체력
    st.session_state.food = 20        # 식량
    st.session_state.material = 10    # 자재 (쉘터 보강용)
    st.session_state.defense = 10     # 쉘터 방어력
    st.session_state.survivors = ["나"] # 동료 리스트
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.log = ["🏕️ 쉘터에 들어왔습니다. 30일 동안 살아남아 구조대를 기다리세요!"]

if "day" not in st.session_state:
    init_game()

# --- 밤 이벤트 및 턴 넘기기 ---
def end_day_action(action_name):
    # 1. 식량 소비 (인원수 비례)
    food_consumed = len(st.session_state.survivors) * 2
    st.session_state.food = max(0, st.session_state.food - food_consumed)
    
    st.session_state.log.append(f"🌅 [Day {st.session_state.day}] 낮 행동: **{action_name}** 완료 (식량 {food_consumed} 소모)")

    # 2. 밤 좀비 습격 이벤트
    if st.session_state.day < 30:
        zombie_attack = random.randint(15, 35)
        net_damage = max(0, zombie_attack - st.session_state.defense)
        
        if net_damage > 0:
            st.session_state.hp -= net_damage
            st.session_state.log.append(f"🌙 밤에 좀비가 습격했습니다! (방어력 부족으로 내 체력 -{net_damage})")
        else:
            st.session_state.log.append(f"🌙 밤에 좀비가 습격했지만, 쉘터가 완벽하게 막아냈습니다!")

        # 3. 무작위 이벤트 (동료 영입 또는 위기)
        event_roll = random.random()
        if event_roll < 0.35 and len(st.session_state.survivors) < 5:
            new_names = ["생존자 민수", "엔지니어 지영", "의무병 현우", "베테랑 수진"]
            available = [n for n in new_names if n not in st.session_state.survivors]
            if available:
                new_colleague = random.choice(available)
                st.session_state.survivors.append(new_colleague)
                st.session_state.log.append(f"✨ 생존 소식을 듣고 **'{new_colleague}'**(이)가 쉘터에 합류했습니다!")
        elif event_roll > 0.8:
            lost_food = random.randint(3, 7)
            st.session_state.food = max(0, st.session_state.food - lost_food)
            st.session_state.log.append(f"⚠️ 쥐가 갉아먹거나 식량 창고가 손상되어 식량 {lost_food}을(를) 잃었습니다.")

        # 패배 조건 체크
        if st.session_state.hp <= 0 or st.session_state.food <= 0:
            st.session_state.game_over = True
            if st.session_state.hp <= 0:
                st.session_state.log.append("☠️ 체력이 바닥나서 사망했습니다... 게임 오버.")
            else:
                st.session_state.log.append("☠️ 식량이 고갈되어 굶어 죽었습니다... 게임 오버.")
        else:
            st.session_state.day += 1
            # 30일 도달 시 승리
            if st.session_state.day > 30:
                st.session_state.victory = True
                st.session_state.log.append("🚁 축하합니다! 30일을 버텨 구출 헬기가 도착했습니다! 승리!")

# --- UI 레이아웃 ---
st.title("🏕️ 쉘터 30일 생존기")
st.caption("동료를 모으고, 자원을 관리하며 30일 동안 버텨 살아남으세요!")

if st.button("🔄 게임 리셋"):
    init_game()
    st.rerun()

st.divider()

# 상단 상태바
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("생존 일수", f"Day {st.session_state.day} / 30")
c2.metric("내 체력", f"{st.session_state.hp} HP")
c3.metric("식량", f"{st.session_state.food} 🥫")
c4.metric("자재", f"{st.session_state.material} 🧱")
c5.metric("방어력", f"{st.session_state.defense} 🛡️")

# 동료 현황 표시
survivor_str = ", ".join(st.session_state.survivors)
st.info(f"👥 **현재 쉘터 인원 ({len(st.session_state.survivors)}명):** {survivor_str}")

st.divider()

# 게임 진행 상태에 따른 화면 분기
if st.session_state.game_over:
    st.error("💀 게임 오버! 위쪽의 '게임 리셋' 버튼을 눌러 다시 도전하세요.")
elif st.session_state.victory:
    st.balloons()
    st.success("🎉 대단합니다! 무사히 30일을 버텨 생존에 성공했습니다!")
else:
    st.subheader("☀️ 낮 행동 선택 (하나만 선택하세요)")
    
    col_a, col_b, col_c = st.columns(3)
    
    # 행동 1: 식량 탐사
    with col_a:
        if st.button("🥫 식량 탐사 나가기\n(식량 +8~15 획득)", use_container_width=True):
            found = random.randint(8, 15)
            st.session_state.food += found
            end_day_action(f"식량 탐사 (식량 +{found})")
            st.rerun()

    # 행동 2: 자재 수집 및 쉘터 보강
    with col_b:
        if st.button("🧱 쉘터 보강하기\n(방어력 +5, 자재 필요)", use_container_width=True, disabled=st.session_state.material < 3):
            st.session_state.material -= 3
            st.session_state.defense += 5
            end_day_action("쉘터 보강 (방어력 +5)")
            st.rerun()
        if st.session_state.material < 3:
            st.caption("⚠️ 자재가 부족합니다 (최소 3 필요)")

    # 행동 3: 자재 탐사
    with col_c:
        if st.button("🛠️ 자재 수집하기\n(자재 +4~8 획득)", use_container_width=True):
            found_mat = random.randint(4, 8)
            st.session_state.material += found_mat
            end_day_action(f"자재 수집 (자재 +{found_mat})")
            st.rerun()

st.divider()

# 이벤트 및 전투 로그
st.subheader("📜 생존 일지")
log_box = "\n".join(reversed(st.session_state.log[-10:]))
st.text_area("일지 내용", value=log_box, height=220, disabled=True)
