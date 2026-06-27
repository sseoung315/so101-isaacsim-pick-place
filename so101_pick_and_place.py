"""
SO-101 Waypoint Pick-and-Place Runner
--------------------------------------
Isaac Sim Script Editor에서 실행하는 용도입니다.

전제 조건
1. /Graphs/Position_Controller/JointCommandArray 가 존재해야 합니다.
2. input0~input5의 순서는 현재 Scene에서 수동으로 확인한 순서여야 합니다.
3. Cube, table, target_table, finger colliders가 이미 Scene에 설정되어 있어야 합니다.
4. 실행 전 Cube를 시작 위치에 다시 놓아야 합니다.

필요 시 아래 GRAPH_NODE_PATH와 WAYPOINTS만 수정하면 됩니다.
"""

import asyncio

import omni.graph.core as og
import omni.kit.app
import omni.timeline


# 현재 Scene에서 생성된 OmniGraph JointCommandArray 노드 경로
GRAPH_NODE_PATH = "/Graphs/Position_Controller/JointCommandArray"

# ---------------------------------------------------------------------------
# Waypoints
# 각 배열은 JointCommandArray의 input0 ~ input5 순서 기준이다.
# 마지막 값은 이 Scene 기준으로 약 0.5 = Open, 0.0 = Close.
# ---------------------------------------------------------------------------
HOME_OPEN = [0.0, 0.0, 0.0, 0.0, 0.0, 0.5]

PRE_GRASP_OPEN = [0.0, 0.0, -0.25, 1.2, 1.5, 0.4]

# Cube 중심과 손가락 사이 위치를 0.34 → 0.3421로 미세 보정한 값
GRASP_OPEN = [0.0, 0.3421, 0.0, 1.2, 1.5, 0.5]
GRASP_CLOSE = [0.0, 0.3421, 0.0, 1.2, 1.5, 0.0]

LIFT_CLOSE = [0.0, 0.01, 0.26, 1.2, 1.5, 0.1]

TRANSFER_CLOSE = [0.5, 0.1, -0.4, 1.2, 1.5, 0.0]

PRE_PLACE_CLOSE = [0.5, 0.4, -0.4, 1.2, 1.5, 0.0]
PLACE_CLOSE = [0.5, 0.45, -0.4, 1.2, 1.5, 0.0]
PLACE_OPEN = [0.5, 0.45, -0.4, 1.2, 1.5, 0.5]

RETREAT_OPEN = [0.5, 0.2, -0.4, 1.2, 1.5, 0.5]


SEQUENCE = [
    ("HOME", HOME_OPEN, 1.0, 0.5),
    ("PRE_GRASP", PRE_GRASP_OPEN, 1.0, 0.3),
    ("GRASP", GRASP_OPEN, 0.8, 0.3),
    ("GRIPPER_CLOSE", GRASP_CLOSE, 0.6, 1.0),
    ("LIFT", LIFT_CLOSE, 1.2, 0.4),
    ("TRANSFER", TRANSFER_CLOSE, 2.0, 0.4),
    ("PRE_PLACE", PRE_PLACE_CLOSE, 1.0, 0.3),
    ("PLACE", PLACE_CLOSE, 1.0, 0.4),
    ("GRIPPER_OPEN", PLACE_OPEN, 0.6, 0.8),
    ("RETREAT", RETREAT_OPEN, 1.0, 0.3),
    ("HOME_RETURN", HOME_OPEN, 1.5, 0.0),
]


def get_command_attributes():
    """JointCommandArray input0~input5 Attribute를 찾아 유효성 검사한다."""
    attributes = []

    for index in range(6):
        path = f"{GRAPH_NODE_PATH}.inputs:input{index}"
        attr = og.Controller.attribute(path)

        if attr is None or not attr.is_valid():
            raise RuntimeError(
                f"Joint command attribute를 찾지 못했습니다: {path}\n"
                "GRAPH_NODE_PATH 또는 Position_Controller Graph 구조를 확인하세요."
            )

        attributes.append(attr)

    return attributes


def read_command_values(attributes):
    """현재 Graph에 저장된 input0~input5 값을 읽는다."""
    values = []

    for attr in attributes:
        value = og.DataView.get(attribute=attr)
        values.append(float(value) if value is not None else 0.0)

    return values


def write_command_values(attributes, values):
    """Graph input0~input5에 관절 목표값을 쓴다."""
    if len(values) != 6:
        raise ValueError("Waypoint는 반드시 6개의 관절값을 가져야 합니다.")

    for attr, value in zip(attributes, values):
        og.DataView.set(attribute=attr, value=float(value))


async def wait_seconds(seconds, fps=60):
    """Isaac Sim 프레임 갱신을 기다린다."""
    frames = max(1, int(seconds * fps))

    for _ in range(frames):
        await omni.kit.app.get_app().next_update_async()


async def move_smooth(attributes, start, target, duration):
    """
    Smoothstep 보간으로 현재 command 값에서 target Waypoint까지 부드럽게 이동한다.
    급격한 관절 명령 변화를 줄여 Cube 파지 안정성을 높인다.
    """
    if len(start) != 6 or len(target) != 6:
        raise ValueError("start와 target은 각각 6개의 값이어야 합니다.")

    steps = max(1, int(duration * 60))

    for step in range(1, steps + 1):
        t = step / steps
        smooth_t = t * t * (3.0 - 2.0 * t)  # smoothstep

        command = [
            q0 + smooth_t * (q1 - q0)
            for q0, q1 in zip(start, target)
        ]

        write_command_values(attributes, command)
        await omni.kit.app.get_app().next_update_async()


async def run_pick_and_place():
    """전체 Pick-and-Place 시퀀스를 실행한다."""
    timeline = omni.timeline.get_timeline_interface()
    attributes = get_command_attributes()

    # 현재 command 입력값을 읽고, HOME 자세부터 부드럽게 시작한다.
    current = read_command_values(attributes)

    if not timeline.is_playing():
        timeline.play()
        await wait_seconds(0.2)

    print("\n=== SO-101 Pick-and-Place Start ===")

    for name, target, move_time, hold_time in SEQUENCE:
        print(f"[MOVE] {name}: {target}")

        await move_smooth(
            attributes=attributes,
            start=current,
            target=target,
            duration=move_time,
        )

        await wait_seconds(hold_time)
        current = target.copy()

    print("=== SO-101 Pick-and-Place Complete ===\n")


# Script Editor에서 실행하면 비동기 시퀀스를 시작한다.
asyncio.ensure_future(run_pick_and_place())
