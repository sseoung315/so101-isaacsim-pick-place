# SO-101 Isaac Sim Pick-and-Place

Isaac Sim에서 SO-101 로봇팔을 사용해 Cube를 집고 `target_table` 위에 내려놓는 Pick-and-Place 프로젝트입니다.

이 프로젝트는 IK나 강화학습 이전 단계로, **수동으로 확보한 관절 Waypoint를 부드럽게 보간하여 자동 실행**합니다.

## 현재 구현 범위

- SO-101 URDF Import 및 Articulation 구성
- OmniGraph `Joint Position Controller` 기반 관절 위치 제어
- Cube의 Rigid Body / Collider 설정
- 양쪽 그리퍼 충돌 형상 보강
- 관절 Drive Damping 튜닝
- Waypoint 기반 Pick-and-Place 자동 실행

## 프로젝트 구조

```text
so101-isaacsim-pick-place/
├── README.md
├── scripts/
│   └── so101_pick_and_place.py
├── docs/
│   ├── scene_setup.md
│   └── troubleshooting.md
└── scene/
    └── README.md
```

## 실행 환경

- Ubuntu
- NVIDIA Isaac Sim 5.1 계열 GUI 환경 기준
- SO-101 URDF: `TheRobotStudio/SO-ARM100` 저장소의 `Simulation/SO101/so101_new_calib.urdf`

로컬 URDF 경로 예시:

```text
/home/hs315/so101_ws/SO-ARM100/Simulation/SO101/so101_new_calib.urdf
```

## 실행 전 Scene 준비

1. SO-101 URDF를 Import한다.
2. Import 시 `Fix Base Link`, `Import as Articulation`, `Create Physics Scene`을 활성화한다.
3. 다음 메뉴로 Position Controller를 만든다.

```text
Tools → Robotics → OmniGraph Controllers → Joint Position
```

4. Graph 경로가 아래와 같은지 확인한다.

```text
/Graphs/Position_Controller/JointCommandArray
```

5. Cube와 그리퍼 Collider, table 및 target_table Collider를 설정한다.
6. Cube를 시작 위치에 다시 놓는다.
7. `scripts/so101_pick_and_place.py` 전체를 Isaac Sim `Window → Script Editor`에 붙여넣고 실행한다.

## Waypoint 순서

```text
HOME_OPEN
→ PRE_GRASP_OPEN
→ GRASP_OPEN
→ GRASP_CLOSE
→ LIFT_CLOSE
→ TRANSFER_CLOSE
→ PRE_PLACE_CLOSE
→ PLACE_CLOSE
→ PLACE_OPEN
→ RETREAT_OPEN
→ HOME_OPEN
```

- 마지막 input 값은 이 Scene 기준으로 `약 0.5 = gripper open`, `약 0.0 = gripper close`이다.
- 모든 관절 목표값은 현재 `JointCommandArray`의 `input0~input5` 순서에 맞춰져 있다.
- 다른 Scene 또는 다른 Graph를 만들었다면 `JointNameArray`로 관절 순서를 먼저 확인해야 한다.

## 핵심 문제와 해결

### 1. Cube가 그리퍼에서 빠지는 문제

초기에는 그리퍼 접촉 형상이 부족하고 관절 진동이 커서 Cube가 Lift 과정에서 자주 이탈했다.

해결:
- 움직이는 손가락 collision mesh에 Collider 추가
- 고정 손가락 아래에 `left_finger_collision` Box Collider 추가
- Cube는 `Rigid Body + Collider`, Approximation은 `Convex Hull`로 설정
- 관절 Damping 증가
- Waypoint 사이를 보간해 급격한 자세 변경을 완화

### 2. 잔진동 문제

Damping이 너무 작으면 목표 자세 주변에서 관절이 미세하게 떨리고, 그 진동이 그리퍼로 전달되어 파지 물체가 이탈한다.

해결:
- Stiffness는 크게 변경하지 않고 Damping을 증가
- 특히 `shoulder_lift`, `elbow_flex`, `wrist_flex`의 Damping을 우선 튜닝
- 이동 시간을 늘리고 필요한 구간은 중간 Waypoint를 추가

### 3. Stop과 Pause 차이

- `Stop`: PhysX 시뮬레이션을 초기화한다. 로봇은 기본 관절 상태로 돌아갈 수 있다.
- `Pause`: 현재 로봇 자세를 유지한 채 Cube 위치, Collider, 물리 설정을 조정할 때 사용한다.

## 다음 확장 단계

1. Pick-and-Place 2~3회 연속 성공 확인
2. 카메라 추가
3. RGB 영상 + 현재 관절값 + 목표 관절값 저장
4. 실제 SO-101 Follower 제작
5. 시뮬레이션과 실제 로봇의 관절각/엔드이펙터/카메라 오차 비교

## References

- SO-101 robot model and URDF are based on  
  [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)  
  Licensed under Apache License 2.0.

- The simulation was developed using  
  [NVIDIA Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/).

- The project roadmap is inspired by  
  [Hugging Face LeRobot](https://github.com/huggingface/lerobot).

## License

The original waypoint control code and project documentation in this repository are released under the MIT License.

SO-101 URDF, meshes, STL files, and other upstream assets are not redistributed in this repository. Please refer to the original SO-ARM100 repository and its license when using those assets.
