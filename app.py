import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쉘터 30일 생존기 (감염 및 동료 조우)", page_icon="🏕️", layout="centered")

# --- 탐험 시 만날 수 있는 전체 후보 동료 풀 ---
ALL_POSSIBLE_RECRUITS = {
    "엔지니어 지영": {"hp": 90, "max_hp": 90, "role": "건축가", "desc": "자재 수집량 +50% 증가"},
    "의무병 현우": {"hp": 75, "max_hp": 75, "role": "군의관", "desc": "매일 밤 팀원 체력 자동 회복"},
    "베테랑 수진": {"hp": 100, "max_hp": 100, "role": "경호원", "desc": "좀비 습격 방어력 +10 버프"},
    "정찰병 도진": {"hp": 85, "max_hp": 85, "role": "스카우트", "desc": "탐험 시 식량 추가 획득"},
    "요리사 은비": {"hp": 70, "max_hp": 70, "role": "영양사", "desc": "식량 소비량 감소 효과"},
    "군인 태성": {"hp": 110, "max_hp": 110, "role": "특전사", "desc": "전투력 및 방어력 대폭 상승"},
}

# --- 게임 상태 초기화 ---
def init_game():
    st.session_state.day = 1
    st.session_state.turn = "낮"  # "낮" 또는 "밤"
    st.session_state.food = 35
    st.session_state.material = 15
    st.session_state.defense = 15
    
    # 기본 동료 설정
    st.session_state.survivors = {
        "나 (플레이어)": {"hp": 100, "max_hp": 100, "role": "리더", "desc": "쉘터의 총책임자"},
        "생존자 민수": {"hp": 80, "max_hp": 80, "role": "식량 수색가", "desc": "식량 탐사 효율 대폭 증가"},
    }
    
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.log = ["🏕️ 쉘터에 정착했습니다. 동료를 늘리고 30일 동안 살아남으세요!"]

# 안전한 초기화 체크
if "day" not in st.session_state or not isinstance(st.session_state.get("survivors"), dict):
    init_game()

# --- 밤 턴 처리 함수 ---
def process_night_turn():
    alive_count = len(st.session_state.survivors)
    
    # 1. 식량 소비 (생존자 1명당 하루 2개)
    food_consumed = alive_count * 2
    st.session_state.food = max(0, st.session_state.food - food_consumed)
    st.session_state.log.append(f"🌙 [Day {st.session_state.day} 밤] 식량 배급 완료 (총 {food_consumed} 소모)")

    # 2. 밤 좀비 습격 이벤트
    if st.session_state.day < 30:
        zombie_attack = random.randint(30, 55)
        extra_defense = 10 if "베테랑 수진" in st.session_state.survivors else 0
        net_damage = max(5, zombie_attack - (st.session_state.defense + extra_defense))
        
        targets = list(st.session_state.survivors.keys())
        hit_target = random.choice(targets)
        
        st.session_state.survivors[hit_target]["hp"] -= net_damage
        st.session_state.log.append(f"💥 밤 습격! 좀비들이 쉘터를 덮쳐 **{hit_target}**(이)가 {net_damage}의 피해를 입었습니다!")

        # 사망자 체크
        dead_members = [name for name, data in st.session_state.survivors.items() if data["hp"] <= 0]
        for dead in dead_members:
            del st.session_state.survivors[dead]
            st.session_state.log.append(f"☠️ 안타깝게도 **{dead}**(이)가 부상을 이기지 못하고 사망했습니다...")

        # 의무병 패시브
        if "의무병 현우" in st.session_state.survivors:
            for name, data in st.session_state.survivors.items():
                data["hp"] = min(data["max_hp"], data["hp"] + 15)
            st.session_state.log.append("🩺 의무병 현우가 밤사이에 동료들의 부상을 치료해 체력을 15 회복시켰습니다.")

        # 3. 극단적 사건 (동료 감염 또는 위기 선택지) 이벤트 발생 확률
        event_roll = random.random()
        
        # 동료가 2명 이상이고, 감염 이벤트가 발생할 확률 (30%)
        if event_roll < 0.3 and len(st.session_state.survivors) > 1:
            # 플레이어("나")를 제외한 동료 중 무작위 감염자 선정
            potential_infected = [n for n in st.session_state.survivors.keys() if n != "나 (플레이어)"]
            if potential_infected:
                infected_target = random.choice(potential_infected)
                st.session_state.log.append(f"🚨 **[긴급 위기]** 야간 경계 중, **{infected_target}**(이)가 좀비에게 물려 **바이러스에 감염**된 사실이 밝혀졌습니다!")
                # 감염 플래그를 세션에 저장하여 다음 낮 턴에 선택지를 띄움
                st.session_state.infected_crisis = infected_target
        elif event_roll > 0.8:
            crisis_type = random.choice(["약탈자", "들쥐 떼", "이상 기온"])
            if crisis_type == "약탈자":
                lost = random.randint(5, 12)
                st.session_state.food = max(0, st.session_state.food - lost)
                st.session_state.log.append(f"⚠️ 야간 약탈자 출몰! 식량창고가 털려 식량 {lost}개를 도둑맞았습니다.")
            elif crisis_type == "들쥐 떼":
                lost_m = random.randint(4, 8)
                st.session_state.material = max(0, st.session_state.material - lost_m)
                st.session_state.log.append(f"⚠️ 들쥐 떼가 자재를 갉아먹어 자재 {lost_m}을(를) 잃었습니다.")
            else:
                st.session_state.defense = max(5, st.session_state.defense - 5)
                st.session_state.log.append(f"⚠️ 매서운 추위에 쉘터 벽면이 손상되어 방어력이 5 감소했습니다.")

        # 게임 오버 조건 체크
        if "나 (플레이어)" not in st.session_state.survivors or st.session_state.food <= 0:
            st.session_state.game_over = True
            if "나 (플레이어)" not in st.session_state.survivors:
                st.session_state.log.append("☠️ 플레이어(리더)가 사망했습니다... 게임 오버.")
            else:
                st.session_state.log.append("☠️ 식량이 완전히 고갈되어 굶어 죽었습니다... 게임 오버.")
        else:
            st.session_state.day += 1
            if st.session_state.day > 30:
                st.session_state.victory = True
                st.session_state.log.append("🚁 축하합니다! 무사히 30일을 버텨 구출되었습니다! 승리!")
            else:
                st.session_state.turn = "낮"
                st.session_state.log.append(f"☀️ [Day {st.session_state.day} 낮] 밝아왔습니다. 오늘의 행동을 선택하세요.")

# --- UI 레이아웃 ---
st.title("🏕️ 쉘터 30일 생존기 (감염 & 동료 조우)")
st.caption("탐험을 통해 새로운 동료를 만나고, 잔혹한 생존 선택지 속에서 살아남으세요!")

if st.button("🔄 게임 리셋"):
    init_game()
    st.rerun()

st.divider()

# 상단 자원 현황
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("생존 일수", f"Day {st.session_state.day} / 30")
c2.metric("현재 턴", f"🌙 {st.session_state.turn}" if st.session_state.turn == "밤" else f"☀️ {st.session_state.turn}")
c3.metric("식량", f"{st.session_state.food} 🥫")
c4.metric("자재", f"{st.session_state.material} 🧱")
c5.metric("방어력", f"{st.session_state.defense} 🛡️")

st.divider()

# 팀원 체력 및 특성 대시보드
st.subheader(f"👥 생존자 부대 현황 ({len(st.session_state.survivors)}명)")
member_cols = st.columns(max(1, len(st.session_state.survivors)))

for idx, (name, data) in enumerate(st.session_state.survivors.items()):
    with member_cols[idx]:
        hp_ratio = max(0.0, data["hp"] / data["max_hp"])
        st.markdown(f"**{name}**")
        st.caption(f"역할: {data['role']}\n({data['desc']})")
        st.progress(hp_ratio)
        st.text(f"HP: {data['hp']} / {data['max_hp']}")

st.divider()

if st.session_state.game_over:
    st.error("💀 게임 오버! 상단의 '게임 리셋' 버튼을 눌러 다시 도전하세요.")
elif st.session_state.victory:
    st.balloons()
    st.success("🎉 대단합니다! 동료 부대와 함께 30일 생존에 성공했습니다!")
else:
    # --- 감염 위기 이벤트 발생 시 강제 선택지 팝업 ---
    if "infected_crisis" in st.session_state and st.session_state.infected_crisis:
        infected_person = st.session_state.infected_crisis
        st.error(f"🚨 **[중대 결정]** 동료 **{infected_person}**(이)가 감염되었습니다! 어떻게 하시겠습니까?")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            if st.button("🏃‍♂️ 동료를 쉘터에서 내쫓는다 (추방)", use_container_width=True, type="primary"):
                if infected_person in st.session_state.survivors:
                    del st.session_state.survivors[infected_person]
                st.session_state.log.append(f"💔 눈물을 머금고 감염된 **{infected_person}**을(를) 쉘터 밖으로 내쫓았습니다...")
                st.session_state.infected_crisis = None
                st.rerurn()
        with col_opt2:
            if st.button("💊 남은 식량/의약품을 몰아주어 치료를 시도한다 (식량 -10)", use_container_width=True, disabled=st.session_state.food < 10):
                st.session_state.food -= 10
                # 50% 확률로 완치 혹은 사망
                if random.random() < 0.5:
                    st.session_state.log.append(f"✨ 기적처럼 **{infected_person}**이(가) 감염을 이겨내고 완치되었습니다!")
                else:
                    if infected_person in st.session_state.survivors:
                        del st.session_state.survivors[infected_person]
                    st.session_state.log.append(f"☠️ 안타깝게도 치료에 실패하여 **{infected_person}**을(를) 잃었습니다...")
                st.session_state.infected_crisis = None
                st.rerurn()
        st.divider()

    # --- 낮 턴 / 밤 턴 UI 분기 ---
    if st.session_state.turn == "낮":
        st.subheader("☀️ 낮 행동 선택 (원하는 활동을 고르세요)")
        
        tab1, tab2, tab3 = st.tabs(["🗺️ 지역 탐사하기 (동료 조우)", "🛠️ 쉘터 관리하기", "🌙 밤으로 넘어가기"])
        
        with tab1:
            st.markdown("### 탐험할 지역을 선택하세요 (새로운 동료를 만날 수 있습니다!)")
            loc_col1, loc_col2, loc_col3 = st.columns(3)
            
            # 지역 1: 대형 마트
            with loc_col1:
                st.markdown("🛒 **대형 마트**")
                st.caption("식량을 얻고, 생존자를 만날 확률이 높습니다.")
                if st.button("마트 탐사", use_container_width=True):
                    found_food = random.randint(15, 25)
                    if "생존자 민수" in st.session_state.survivors:
                        found_food += 8
                    st.session_state.food += found_food
                    
                    # 탐험 시 새로운 동료 조우 판정 (40% 확률)
                    event_msg = f"🛒 마트를 수색해 식량 {found_food}개를 획득했습니다."
                    if random.option := (random.random() < 0.4) and len(st.session_state.survivors) < 6:
                        available_recruits = [k for k in ALL_POSSIBLE_RECRUITS.keys() if k not in st.session_state.survivors]
                        if available_recruits:
                            new_friend = random.choice(available_recruits)
                            st.session_state.survivors[new_friend] = ALL_POSSIBLE_RECRUITS[new_friend]
                            event_msg += f" 그리고 숨어있던 **'{new_friend}'({ALL_POSSIBLE_RECRUITS[new_friend]['role']})**을(를) 극적으로 만나 합류시켰습니다!"
                    
                    st.session_state.log.append(event_msg)
                    st.session_state.turn = "밤"
                    st.rerun()

            # 지역 2: 철물점/공사장
            with loc_col2:
                st.markdown("🏗️ **공사장 및 철물점**")
                st.caption("자재를 수집하며 동료를 발견할 수 있습니다.")
                if st.button("공사장 탐사", use_container_width=True):
                    found_mat = random.randint(8, 15)
                    if "엔지니어 지영" in st.session_state.survivors:
                        found_mat += 6
                    st.session_state.material += found_mat
                    
                    event_msg = f"🏗️ 공사장에서 자재 {found_mat}개를 수집했습니다."
                    if random.random() < 0.4 and len(st.session_state.survivors) < 6:
                        available_recruits = [k for k in ALL_POSSIBLE_RECRUITS.keys() if k not in st.session_state.survivors]
                        if available_recruits:
                            new_friend = random.choice(available_recruits)
                            st.session_state.survivors[new_friend] = ALL_POSSIBLE_RECRUITS[new_friend]
                            event_msg += f" 또한 일용 건물에 숨어있던 **'{new_friend}'**을(를) 영입했습니다!"

                    st.session_state.log.append(event_msg)
                    st.session_state.turn = "밤"
                    st.rerun()

            # 지역 3: 버려진 병원
            with loc_col3:
                st.markdown("🏥 **버려진 병원**")
                st.caption("위험하지만 동료를 치료하거나 생존자를 찾습니다.")
                if st.button("병원 탐사", use_container_width=True):
                    heal_amt = random.randint(20, 35)
                    for name in st.session_state.survivors:
                        st.session_state.survivors[name]["hp"] = min(
                            st.session_state.survivors[name]["max_hp"],
                            st.session_state.survivors[name]["hp"] + heal_amt
                        )
                    
                    event_msg = f"🏥 병원에서 팀원의 체력이 {heal_amt} 회복되었습니다."
                    if random.random() < 0.45 and len(st.session_state.survivors) < 6:
                        available_recruits = [k for k in ALL_POSSIBLE_RECRUITS.keys() if k not in st.session_state.survivors]
                        if available_recruits:
                            new_friend = random.choice(available_recruits)
                            st.session_state.survivors[new_friend] = ALL_POSSIBLE_RECRUITS[new_friend]
                            event_msg += f" 병실에 고립되어 있던 **'{new_friend}'**을(를) 구출했습니다!"

                    st.session_state.log.append(event_msg)
                    st.session_state.turn = "밤"
                    st.rerun()

        with tab2:
            st.markdown("### 쉘터 내부 작업")
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if st.button("🧱 쉘터 견고하게 보강하기\n(자재 -4 ➔ 방어력 +10)", use_container_width=True, disabled=st.session_state.material < 4):
                    st.session_state.material -= 4
                    st.session_state.defense += 10
                    st.session_state.log.append("🧱 쉘터를 튼튼하게 보강하여 방어력이 10 증가했습니다.")
                    st.session_state.turn = "밤"
                    st.rerun()
                if st.session_state.material < 4:
                    st.caption("⚠️ 자재가 부족합니다 (최소 4 필요)")

            with m_col2:
                if st.button("🩹 비상 응급 치료\n(식량 -6 ➔ 팀 체력 전체 +35)", use_container_width=True, disabled=st.session_state.food < 6):
                    st.session_state.food -= 6
                    for name in st.session_state.survivors:
                        st.session_state.survivors[name]["hp"] = min(
                            st.session_state.survivors[name]["max_hp"],
                            st.session_state.survivors[name]["hp"] + 35
                        )
                    st.session_state.log.append("🩹 비상 식량을 소모해 팀원 전체를 응급 치료했습니다.")
                    st.session_state.turn = "밤"
                    st.rerun()
                if st.session_state.food < 6:
                    st.caption("⚠️ 식량이 부족합니다 (최소 6 필요)")

        with tab3:
            st.markdown("### 휴식 및 야간 진입")
            st.write("특별한 활동 없이 휴식을 취하며 밤의 위기를 맞이합니다.")
            if st.button("🌙 바로 밤으로 넘어가기", type="primary", use_container_width=True):
                st.session_state.log.append(f"☀️ 낮 동안 조용히 휴식을 취하며 체력을 비축했습니다.")
                st.session_state.turn = "밤"
                st.rerun()

    else:
        # 밤 턴 처리 화면
        st.subheader("🌙 밤 턴: 좀비의 습격 시간")
        st.warning("해가 지고 좀비들이 움직이기 시작합니다. 밤 동안 무슨 일이 일어날지 확인하세요!")
        
        if st.button("▶️ 밤 이벤트 및 결과 확인하기", type="primary", use_container_width=True):
            process_night_turn()
            st.rerun()

st.divider()

# 생존 일지
st.subheader("📜 생존 일지")
log_box = "\n".join(reversed(st.session_state.log[-10:]))
st.text_area("일지 내용", value=log_box, height=220, disabled=True)
