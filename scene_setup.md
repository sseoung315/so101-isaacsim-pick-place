# Scene Setup

## 1. SO-101 Import

사용 URDF:

```text
/home/hs315/so101_ws/SO-ARM100/Simulation/SO101/so101_new_calib.urdf
```

Import 권장값:

- Import as Articulation: On
- Fix Base Link: On
- Create Physics Scene: On
- Merge Fixed Joints: On

## 2. Position Controller 생성

```text
Tools → Robotics → OmniGraph Controllers → Joint Position
```

Robot Prim에 SO-101 최상위 Prim을 선택한다.

생성 후 아래 노드가 있어야 한다.

```text
/Graphs/Position_Controller/JointCommandArray
```

## 3. 물리 설정

### Cube

```text
Rigid Body: On
Collider: On
Approximation: Convex Hull
Mass: 0.01 ~ 0.02 kg
```

### table / target_table / GroundPlane

```text
Collider: On
Rigid Body: Off
```

## 4. 그리퍼 Collider

### 움직이는 손가락

```text
moving_jaw_so101_v1_link
└── collisions
    └── Collider
```

### 고정 손가락

```text
gripper_frame_link
└── left_finger_collision
    └── Collider
```

`left_finger_collision`은 손가락 안쪽 접촉면에 배치한다.

- 얇고 긴 Box 형태
- Rigid Body는 추가하지 않음
- Collider Approximation: Bounding Cube 또는 Convex Hull

## 5. 위치 조정 팁

- Play 중에는 Cube가 Collider와 충돌해 원하는 위치로 이동하지 않을 수 있다.
- 이때 Stop을 누르면 로봇이 초기 상태로 돌아갈 수 있다.
- 현재 자세를 유지하려면 Pause를 사용한다.
- Pause 상태에서 Cube의 Rigid Body 또는 Collider를 잠시 Disable하고 위치를 맞춘 뒤 다시 Enable한다.
