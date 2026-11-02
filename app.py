import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쉘터 30일 생존기 (탐험 & 낮/밤 구별)", page_icon="🏕️", layout="centered")

# --- 게임 상태 초기화 ---
def init_game():
    st.session_state.day = 1
    st.session_state.turn = "낮"  # "낮" 또는 "밤"
    st.session_state.food = 35
    st.session_state.material = 15
    st.session_state.defense = 15
    
    # 동료 설정
    st.session_state.survivors = {
        "나 (플레이어)": {"hp": 100, "max_hp": 100, "role": "리더", "desc": "쉘터의 총책임자"},
        "생존자 민수": {"hp": 80, "max_hp": 80, "role": "식량 수색가", "desc": "식량 탐사 효율 대폭 증가"},
    }
    
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.log = ["🏕️ 쉘터에 정착했습니다. 낮에는 지역을 탐색하고, 밤에는 좀비의 습격을 버텨내세요!"]

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
        
        # 피해 대상 무작위 지정
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

        # 3. 고 빈도 무작위 이벤트 (이벤트 확률 대폭 상향)
        event_roll = random.random()
        if event_roll < 0.6 and len(st.session_state.survivors) < 6:
            possible_new = {
                "엔지니어 지영": {"hp": 90, "max_hp": 90, "role": "건축가", "desc": "자재 수집량 +50% 증가"},
                "의무병 현우": {"hp": 75, "max_hp": 75, "role": "군의관", "desc": "매일 밤 팀원 체력 자동 회복"},
                "베테랑 수진": {"hp": 100, "max_hp": 100, "role": "경호원", "desc": "좀비 습격 방어력 +10 버프"},
            }
            available = [n for n in possible_new.keys() if n not in st.session_state.survivors]
            if available:
                new_colleague = random.choice(available)
                st.session_state.survivors[new_colleague] = possible_new[new_colleague]
                st.session_state.log.append(f"✨ 위기 속에서 생존한 **'{new_colleague}'({possible_new[new_colleague]['role']})**(이)가 쉘터로 찾아왔습니다!")
        elif event_roll > 0.75:
            # 돌발 위기 이벤트
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
st.title("🏕️ 쉘터 30일 생존기 (탐험 & 낮/밤 시스템)")
st.caption("낮에는 지역을 골라 탐험하고, 밤에는 쉘터를 지켜내며 30일을 살아남으세요!")

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
    # --- 낮 턴 / 밤 턴 UI 분기 ---
    if st.session_state.turn == "낮":
        st.subheader("☀️ 낮 행동 선택 (원하는 활동을 고르세요)")
        
        tab1, tab2, tab3 = st.tabs(["🗺️ 지역 탐사하기", "🛠️ 쉘터 관리하기", "🌙 밤으로 넘어가기"])
        
        with tab1:
            st.markdown("### 탐험할 지역을 선택하세요")
            loc_col1, loc_col2, loc_col3 = st.columns(3)
            
            # 지역 1: 대형 마트 (식량 대량 획득, 위험 보통)
            with loc_col1:
                st.markdown("🛒 **대형 마트**")
                st.caption("식량을 많이 얻을 수 있지만 약간의 위험이 따릅니다.")
                if st.button("마트 탐사", use_container_width=True):
                    found_food = random.randint(15, 25)
                    if "생존자 민수" in st.session_state.survivors:
                        found_food += 10
                    st.session_state.food += found_food
                    
                    # 무작위로 소모 데미지 발생 가능성
                    if random.random() < 0.3:
                        st.session_state.survivors["나 (플레이어)"]["hp"] = max(0, st.session_state.survivors["나 (플레이어)"]["hp"] - 10)
                        st.session_state.log.append(f"🛒 마트 탐사 중 좀비와 조우해 플레이어가 10의 피해를 입었지만 식량 {found_food}개를 챙겼습니다!")
                    else:
                        st.session_state.log.append(f"🛒 안전하게 대형 마트를 털어 식량 {found_food}개를 획득했습니다!")
                    st.session_state.turn = "밤"
                    st.rerun()

            # 지역 2: 철물점/공사장 (자재 대량 획득)
            with loc_col2:
                st.markdown("🏗️ **공사장 및 철물점**")
                st.caption("쉘터 보강에 필요한 자재를 대량으로 수집합니다.")
                if st.button("공사장 탐사", use_container_width=True):
                    found_mat = random.randint(8, 15)
                    if "엔지니어 지영" in st.session_state.survivors:
                        found_mat += 8
                    st.session_state.material += found_mat
                    st.session_state.log.append(f"🏗️ 공사장에서 철재와 도구를 수색해 자재 {found_mat}개를 획득했습니다!")
                    st.session_state.turn = "밤"
                    st.rerun()

            # 지역 3: 병원 (의약품 / 체력 회복 또는 이벤트)
            with loc_col3:
                st.markdown("🏥 **버려진 병원**")
                st.caption("위험하지만 다친 동료를 치료하거나 구급품을 얻습니다.")
                if st.button("병원 탐사", use_container_width=True):
                    heal_amt = random.randint(20, 40)
                    for name in st.session_state.survivors:
                        st.session_state.survivors[name]["hp"] = min(
                            st.session_state.survivors[name]["max_hp"],
                            st.session_state.survivors[name]["hp"] + heal_amt
                        )
                    st.session_state.log.append(f"🏥 병원에서 의약품을 찾아내 팀원 전체의 체력이 {heal_amt} 회복되었습니다!")
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
