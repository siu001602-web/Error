import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쉘터 30일 생존기 (확장판)", page_icon="🏕️", layout="centered")

# --- 10명의 새로운 동료 풀 ---
ALL_POSSIBLE_RECRUITS = {
    "엔지니어 지영": {"hp": 90, "max_hp": 90, "role": "건축가", "desc": "자재 수집량 증가"},
    "의무병 현우": {"hp": 75, "max_hp": 75, "role": "군의관", "desc": "매일 밤 팀원 체력 자동 회복"},
    "베테랑 수진": {"hp": 100, "max_hp": 100, "role": "경호원", "desc": "좀비 습격 방어력 버프"},
    "정찰병 도진": {"hp": 85, "max_hp": 85, "role": "스카우트", "desc": "탐험 시 식량 추가 획득"},
    "요리사 은비": {"hp": 70, "max_hp": 70, "role": "영양사", "desc": "식량 소모량 안정화"},
    "군인 태성": {"hp": 110, "max_hp": 110, "role": "특전사", "desc": "전투력 및 방어력 상승"},
    "과학자 민준": {"hp": 65, "max_hp": 65, "role": "연구원", "desc": "치료 및 응급 효율 증가"},
    "소방관 상욱": {"hp": 105, "max_hp": 105, "role": "구조대원", "desc": "재난 이벤트 피해 경감"},
    "해커 유진": {"hp": 60, "max_hp": 60, "role": "정보원", "desc": "안전한 지역 선별 능력"},
    "농부 하은": {"hp": 80, "max_hp": 80, "role": "농경 전문가", "desc": "식량 탐사 대박 확률 증가"}
}

# --- 탐험 가능한 모든 지역 풀 ---
ALL_LOCATIONS = {
    "🛒 대형 마트": {"type": "food", "desc": "식량을 대량으로 얻을 수 있는 곳입니다."},
    "🏗️ 공사장": {"type": "material", "desc": "쉘터 보강용 자재를 수집할 수 있습니다."},
    "🏥 버려진 병원": {"type": "heal", "desc": "다친 동료를 치료하고 의약품을 찾습니다."},
    "🔫 군부대 보급소": {"type": "defense", "desc": "강력한 방어구와 무기를 얻을 수 있습니다."},
    "💊 대형 약국": {"type": "heal_food", "desc": "식량과 응급 의약품을 동시에 찾습니다."},
    "📚 시립 도서관": {"type": "material_food", "desc": "생존 서적과 비상식량을 얻을 수 있습니다."}
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
        "생존자 민수": {"hp": 80, "max_hp": 80, "role": "식량 수색가", "desc": "식량 탐사 효율 증가"},
    }
    
    # 추모비 리스트 (사망/추방된 인물 기록)
    st.session_state.memorials = []
    
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.log = ["🏕️ 쉘터에 정착했습니다. 다양한 지역을 탐험하고 30일을 버텨내세요!"]

if "day" not in st.session_state or not isinstance(st.session_state.get("survivors"), dict):
    init_game()

# --- 밤 턴 및 재난 이벤트 처리 함수 ---
def process_night_turn():
    alive_count = len(st.session_state.survivors)
    
    # 1. 식량 소비
    food_consumed = alive_count * 2
    st.session_state.food = max(0, st.session_state.food - food_consumed)
    st.session_state.log.append(f"🌙 [Day {st.session_state.day} 밤] 식량 배급 완료 (총 {food_consumed} 소모)")

    # 2. 밤좀비 습격 및 재난 이벤트
    if st.session_state.day < 30:
        zombie_attack = random.randint(25, 50)
        extra_defense = 10 if "베테랑 수진" in st.session_state.survivors else 0
        if "군인 태성" in st.session_state.survivors:
            extra_defense += 10
            
        net_damage = max(5, zombie_attack - (st.session_state.defense + extra_defense))
        
        targets = list(st.session_state.survivors.keys())
        hit_target = random.choice(targets)
        
        st.session_state.survivors[hit_target]["hp"] -= net_damage
        st.session_state.log.append(f"💥 밤 습격! 좀비들이 쉘터를 덮쳐 **{hit_target}**(이)가 {net_damage}의 피해를 입었습니다!")

        # 사망자 체크 및 추모비 등록
        dead_members = [name for name, data in st.session_state.survivors.items() if data["hp"] <= 0]
        for dead in dead_members:
            st.session_state.memorials.append(f"⚰️ {dead} ({st.session_state.survivors[dead]['role']}) - Day {st.session_state.day} 야간 작전/습격 중 사망")
            del st.session_state.survivors[dead]
            st.session_state.log.append(f"☠️ 안타깝게도 **{dead}**(이)가 부상을 이기지 못하고 사망했습니다...")

        # 의무병 패시브
        if "의무병 현우" in st.session_state.survivors:
            for name, data in st.session_state.survivors.items():
                data["hp"] = min(data["max_hp"], data["hp"] + 15)
            st.session_state.log.append("🩺 의무병 현우가 밤사이에 동료들의 부상을 치료해 체력을 회복시켰습니다.")

        # 3. 돌발 사건 및 감염 이벤트
        event_roll = random.random()
        
        if event_roll < 0.12 and len(st.session_state.survivors) > 1:
            potential_infected = [n for n in st.session_state.survivors.keys() if n != "나 (플레이어)"]
            if potential_infected:
                infected_target = random.choice(potential_infected)
                st.session_state.log.append(f"🚨 **[긴급 위기]** 야간 경계 중, **{infected_target}**(이)가 바이러스에 감염되었습니다!")
                st.session_state.infected_crisis = infected_target
        elif event_roll > 0.65:
            disaster = random.choice(["폭우 붕괴", "들쥐 떼 습격", "강력한 좀비 무리 침입", "의문의 화재"])
            if disaster == "폭우 붕괴":
                st.session_state.defense = max(5, st.session_state.defense - 8)
                st.session_state.log.append("🌧️ 거센 폭우로 인해 쉘터 외벽이 무너져 내렸습니다! (방어력 -8)")
            elif disaster == "들쥐 떼 습격":
                lost = random.randint(6, 12)
                st.session_state.food = max(0, st.session_state.food - lost)
                st.session_state.log.append(f"🐀 들쥐 떼가 창고를 습격해 비상식량 {lost}개를 잃었습니다.")
            elif disaster == "강력한 좀비 무리 침입":
                st.session_state.material = max(0, st.session_state.material - 5)
                st.session_state.log.append("🧟 대규모 좀비 무리가 바리케이드를 부수고 침입해 자재 5개를 파손했습니다.")
            else:
                lost_m = random.randint(4, 8)
                st.session_state.material = max(0, st.session_state.material - lost_m)
                st.session_state.log.append(f"🔥 의문의 화재 발생으로 자재 {lost_m}개가 소실되었습니다.")

        # 게임 오버 체크
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
st.title("🏕️ 쉘터 30일 생존기 (확장판)")
st.caption("새로운 지역 탐험, 재난 극복, 그리고 동료들과 함께 30일을 살아남으세요!")

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

# 팀원 체력 대시보드
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
    # --- 감염 위기 선택지 ---
    if "infected_crisis" in st.session_state and st.session_state.infected_crisis:
        infected_person = st.session_state.infected_crisis
        st.error(f"🚨 **[중대 결정]** 동료 **{infected_person}**(이)가 감염되었습니다! 어떻게 하시겠습니까?")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            if st.button("🏃‍♂️ 동료를 쉘터에서 내쫓는다 (추방)", use_container_width=True, type="primary"):
                if infected_person in st.session_state.survivors:
                    st.session_state.memorials.append(f"🚶‍♂️ {infected_person} ({st.session_state.survivors[infected_person]['role']}) - Day {st.session_state.day} 감염으로 인한 추방")
                    del st.session_state.survivors[infected_person]
                st.session_state.log.append(f"💔 눈물을 머금고 감염된 **{infected_person}**을(를) 쉘터 밖으로 추방했습니다...")
                st.session_state.infected_crisis = None
                st.rerun()
        with col_opt2:
            if st.button("💊 의약품을 몰아주어 치료 시도 (식량 -10)", use_container_width=True, disabled=st.session_state.food < 10):
                st.session_state.food -= 10
                if random.random() < 0.6:
                    st.session_state.log.append(f"✨ 기적처럼 **{infected_person}**이(가) 감염을 이겨내고 완치되었습니다!")
                else:
                    if infected_person in st.session_state.survivors:
                        st.session_state.memorials.append(f"⚰️ {infected_person} ({st.session_state.survivors[infected_person]['role']}) - Day {st.session_state.day} 바이러스 치료 실패로 사망")
                        del st.session_state.survivors[infected_person]
                    st.session_state.log.append(f"☠️ 안타깝게도 치료에 실패하여 **{infected_person}**을(를) 잃었습니다...")
                st.session_state.infected_crisis = None
                st.rerun()
        st.divider()

    # --- 낮 턴 / 밤 턴 UI 분기 ---
    if st.session_state.turn == "낮":
        st.subheader("☀️ 낮 행동 선택")
        
        tab1, tab2, tab3 = st.tabs(["🗺️ 랜덤 지역 탐사하기", "🛠️ 쉘터 관리하기", "🌙 밤으로 넘어가기"])
        
        with tab1:
            st.markdown("### 오늘 수색 가능한 지역 (랜덤 3곳)")
            st.caption("매번 탐색할 때마다 무작위 지역이 나타납니다. 원하시는 곳을 선택하세요!")
            
            if "current_random_locations" not in st.session_state or st.session_state.get("refreshed_loc") != st.session_state.day:
                st.session_state.current_random_locations = random.sample(list(ALL_LOCATIONS.keys()), 3)
                st.session_state.refreshed_loc = st.session_state.day
                
            loc_cols = st.columns(3)
            for idx, loc_name in enumerate(st.session_state.current_random_locations):
                loc_info = ALL_LOCATIONS[loc_name]
                with loc_cols[idx]:
                    st.markdown(f"**{loc_name}**")
                    st.caption(loc_info["desc"])
                    if st.button(f"탐사하기", key=f"loc_{idx}", use_container_width=True):
                        event_msg = f"🗺️ {loc_name} 탐사 완료."
                        
                        if loc_info["type"] == "food":
                            f_found = random.randint(18, 28)
                            st.session_state.food += f_found
                            event_msg += f" 식량 {f_found}개를 획득했습니다!"
                        elif loc_info["type"] == "material":
                            m_found = random.randint(10, 18)
                            st.session_state.material += m_found
                            event_msg += f" 자재 {m_found}개를 수집했습니다!"
                        elif loc_info["type"] == "heal":
                            h_found = random.randint(25, 40)
                            for s_name in st.session_state.survivors:
                                st.session_state.survivors[s_name]["hp"] = min(
                                    st.session_state.survivors[s_name]["max_hp"],
                                    st.session_state.survivors[s_name]["hp"] + h_found
                                )
                            event_msg += f" 팀원 전체 체력이 {h_found} 회복되었습니다!"
                        elif loc_info["type"] == "defense":
                            st.session_state.defense += 8
                            st.session_state.material += 5
                            event_msg += " 방어력 +8 및 자재 5개를 획득했습니다!"
                        elif loc_info["type"] == "heal_food":
                            st.session_state.food += 12
                            for s_name in st.session_state.survivors:
                                st.session_state.survivors[s_name]["hp"] = min(
                                    st.session_state.survivors[s_name]["max_hp"],
                                    st.session_state.survivors[s_name]["hp"] + 15
                                )
                            event_msg += " 식량 12개와 소량의 체력을 회복했습니다!"
                        else:
                            st.session_state.food += 10
                            st.session_state.material += 8
                            event_msg += " 식량 10개와 자재 8개를 획득했습니다!"

                        # 🌟 동료 조우 확률 원복 (35% 적용)
                        if random.random() < 0.35 and len(st.session_state.survivors) < 7:
                            available_recruits = [k for k in ALL_POSSIBLE_RECRUITS.keys() if k not in st.session_state.survivors]
                            if available_recruits:
                                new_friend = random.choice(available_recruits)
                                st.session_state.survivors[new_friend] = ALL_POSSIBLE_RECRUITS[new_friend]
                                event_msg += f"  ✨ 그리고 생존자인 **'{new_friend}'({ALL_POSSIBLE_RECRUITS[new_friend]['role']})**을(를) 만나 합류시켰습니다!"

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
                st.session_state.log.append("☀️ 낮 동안 조용히 휴식을 취하며 체력을 비축했습니다.")
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
st.text_area("일지 내용", value=log_box, height=200, disabled=True)

# --- 추모비 (명예의 전당) 영역 ---
if st.session_state.memorials:
    st.divider()
    st.subheader("🕯️ 생존자 추모비 (명예의 전당)")
    st.caption("안타깝게 세상을 떠났거나 쉘터를 떠난 동료들을 기리는 공간입니다.")
    memorial_box = "\n".join(reversed(st.session_state.memorials))
    st.text_area("추모 기록", value=memorial_box, height=120, disabled=True)
