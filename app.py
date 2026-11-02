import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쉘터 30일 생존기 (동료 특성 강화)", page_icon="🏕️", layout="centered")

# --- 게임 상태 초기화 ---
def init_game():
    st.session_state.day = 1
    st.session_state.food = 30
    st.session_state.material = 15
    st.session_state.defense = 15
    
    # 초기 동료 설정 (이름, 체력, 최대체력, 역할, 설명)
    st.session_state.survivors = {
        "나 (플레이어)": {"hp": 100, "max_hp": 100, "role": "리더", "desc": "쉘터의 총책임자"},
        "생존자 민수": {"hp": 80, "max_hp": 80, "role": "식량 수색가", "desc": "식량 탐사 효율 대폭 증가"},
    }
    
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.log = ["🏕️ 든든한 동료들과 함께 쉘터에 정착했습니다. 30일 동안 버텨보세요!"]

if "day" not in st.session_state:
    init_game()

# --- 밤 이벤트 및 턴 넘기기 ---
def end_day_action(action_name):
    alive_count = len(st.session_state.survivors)
    
    # 1. 식량 소비 (생존자 1명당 하루 2개)
    food_consumed = alive_count * 2
    st.session_state.food = max(0, st.session_state.food - food_consumed)
    
    st.session_state.log.append(f"🌅 [Day {st.session_state.day}] 낮 행동: **{action_name}** 완료 (식량 {food_consumed} 소모)")

    # 2. 밤 좀비 습격 이벤트
    if st.session_state.day < 30:
        zombie_attack = random.randint(25, 45)
        
        # 베테랑 수진이 있으면 추가 방어력 적용
        extra_defense = 10 if "베테랑 수진" in st.session_state.survivors else 0
        net_damage = max(5, zombie_attack - (st.session_state.defense + extra_defense))
        
        # 피해 대상 무작위 지정
        targets = list(st.session_state.survivors.keys())
        hit_target = random.choice(targets)
        
        st.session_state.survivors[hit_target]["hp"] -= net_damage
        st.session_state.log.append(f"🌙 밤에 좀비 습격! **{hit_target}**(이)가 {net_damage}의 피해를 입었습니다!")

        # 사망자 체크
        dead_members = [name for name, data in st.session_state.survivors.items() if data["hp"] <= 0]
        for dead in dead_members:
            del st.session_state.survivors[dead]
            st.session_state.log.append(f"☠️ 안타깝게도 **{dead}**(이)가 부상을 이기지 못하고 사망했습니다...")

        # 의무병 현우가 있으면 매일 밤 팀원 체력 자동 회복 패시브 발동
        if "의무병 현우" in st.session_state.survivors:
            for name, data in st.session_state.survivors.items():
                data["hp"] = min(data["max_hp"], data["hp"] + 10)
            st.session_state.log.append("🩺 의무병 현우의 케어로 모든 동료의 체력이 10 회복되었습니다.")

        # 무작위 이벤트 (동료가 많을수록 영입 확률 상승)
        event_roll = random.random()
        recruit_chance = 0.4 + (alive_count * 0.05)
        
        if event_roll < recruit_chance and len(st.session_state.survivors) < 6:
            possible_new = {
                "엔지니어 지영": {"hp": 90, "max_hp": 90, "role": "건축가", "desc": "자재 수집량 +50% 증가"},
                "의무병 현우": {"hp": 75, "max_hp": 75, "role": "군의관", "desc": "매일 밤 팀원 체력 자동 회복"},
                "베테랑 수진": {"hp": 100, "max_hp": 100, "role": "경호원", "desc": "좀비 습격 방어력 +10 버프"},
            }
            available = [n for n in possible_new.keys() if n not in st.session_state.survivors]
            if available:
                new_colleague = random.choice(available)
                st.session_state.survivors[new_colleague] = possible_new[new_colleague]
                st.session_state.log.append(f"✨ 든든한 특기를 가진 **'{new_colleague}'({possible_new[new_colleague]['role']})**(이)가 합류했습니다!")
        elif event_roll > 0.85:
            lost_food = random.randint(4, 9)
            st.session_state.food = max(0, st.session_state.food - lost_food)
            st.session_state.log.append(f"⚠️ 약탈자가 창고를 습격해 식량 {lost_food}을(를) 잃었습니다.")

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
                st.session_state.log.append("🚁 축하합니다! 30일을 버텨 구출되었습니다! 승리!")

# --- UI 레이아웃 ---
st.title("🏕️ 쉘터 30일 생존기 (특성 부대 시스템)")
st.caption("동료를 모으고 특성을 조합해 30일 동안 살아남으세요!")

if st.button("🔄 게임 리셋"):
    init_game()
    st.rerun()

st.divider()

# 상단 자원 현황
c1, c2, c3, c4 = st.columns(4)
c1.metric("생존 일수", f"Day {st.session_state.day} / 30")
c2.metric("식량", f"{st.session_state.food} 🥫")
c3.metric("자재", f"{st.session_state.material} 🧱")
c4.metric("쉘터 방어력", f"{st.session_state.defense} 🛡️")

st.divider()

# 👥 팀원 체력 및 특성 대시보드
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
    st.subheader("☀️ 낮 행동 선택")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    # 행동 1: 식량 탐사 (민수 패시브 적용)
    with col_a:
        base_food = random.randint(12, 18)
        bonus_text = ""
        if "생존자 민수" in st.session_state.survivors:
            base_food += 8
            bonus_text = " (민수 버프 +8)"
            
        if st.button(f"🥫 식량 탐사\n(식량 +{base_food})", use_container_width=True):
            st.session_state.food += base_food
            end_day_action(f"식량 탐사{bonus_text} (식량 +{base_food})")
            st.rerun()

    # 행동 2: 쉘터 보강
    with col_b:
        if st.button("🧱 쉘터 보강\n(방어력 +8)", use_container_width=True, disabled=st.session_state.material < 4):
            st.session_state.material -= 4
            st.session_state.defense += 8
            end_day_action("쉘터 보강 (방어력 +8)")
            st.rerun()
        if st.session_state.material < 4:
            st.caption("⚠️ 자재 필요 (4)")

    # 행동 3: 자재 수집 (지영 패시브 적용)
    with col_c:
        base_mat = random.randint(6, 10)
        mat_bonus_text = ""
        if "엔지니어 지영" in st.session_state.survivors:
            base_mat += 6
            mat_bonus_text = " (지영 버프 +6)"
            
        if st.button(f"🛠️ 자재 수집\n(자재 +{base_mat})", use_container_width=True):
            st.session_state.material += base_mat
            end_day_action(f"자재 수집{mat_bonus_text} (자재 +{base_mat})")
            st.rerun()

    # 행동 4: 응급 치료
    with col_d:
        if st.button("🩹 응급 치료\n(식량 -6, 팀 체력+30)", use_container_width=True, disabled=st.session_state.food < 6):
            st.session_state.food -= 6
            for name in st.session_state.survivors:
                st.session_state.survivors[name]["hp"] = min(
                    st.session_state.survivors[name]["max_hp"], 
                    st.session_state.survivors[name]["hp"] + 30
                )
            end_day_action("응급 치료 (팀원 전체 체력 회복)")
            st.rerun()
        if st.session_state.food < 6:
            st.caption("⚠️ 식량 부족 (6)")

st.divider()

# 생존 일지
st.subheader("📜 생존 일지")
log_box = "\n".join(reversed(st.session_state.log[-10:]))
st.text_area("일지 내용", value=log_box, height=220, disabled=True)
