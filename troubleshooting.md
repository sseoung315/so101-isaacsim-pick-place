# Troubleshooting

## Cube가 Lift 중 그리퍼에서 빠짐

확인 순서:

1. Cube에 `Rigid Body + Collider`가 있는지 확인
2. Cube Collider Approximation이 `Convex Hull`인지 확인
3. 양쪽 손가락 Collider가 있는지 확인
4. Cube가 손가락 Collider와 시작부터 겹치지 않는지 확인
5. Cube 질량을 `0.01 ~ 0.02 kg` 수준으로 낮춰 테스트
6. 그리퍼를 닫은 뒤 0.5~1초 대기
7. Lift 속도를 낮추거나 중간 Waypoint를 추가

## 로봇이 목표 자세 근처에서 떨림

원인:
- 관절 Drive Damping이 너무 작음
- Stiffness 대비 감쇠가 부족함

해결:
- `shoulder_lift`, `elbow_flex`, `wrist_flex`의 Damping부터 증가
- Stiffness는 한 번에 크게 바꾸지 않음
- 목표 자세로의 이동 시간을 늘림

## Stop을 누르면 로봇이 0 자세로 돌아감

정상 동작이다.

- Stop: 물리 시뮬레이션 초기화
- Pause: 현재 물리 상태 유지

Cube 위치를 조정하면서 로봇 자세를 유지하려면 Pause를 사용한다.

## shoulder_pan이 안 움직임

가능한 원인:
- 로봇 베이스 또는 링크가 table Collider와 겹침
- input 순서가 생각한 관절 순서와 다름
- Joint Drive 힘 또는 Damping 설정 문제

확인:
1. table Collider를 잠시 Disable
2. shoulder_pan 입력값을 ±0.2 정도로 변경
3. 회전이 돌아오면 table과 로봇의 충돌 위치를 조정
4. `JointNameArray`에서 input과 관절 이름의 매핑 확인

## 실행 스크립트가 Graph를 못 찾음

`scripts/so101_pick_and_place.py`의 아래 값을 확인한다.

```python
GRAPH_NODE_PATH = "/Graphs/Position_Controller/JointCommandArray"
```

Stage에서 실제 Graph 경로가 다르면 이 문자열만 현재 경로에 맞게 수정한다.
