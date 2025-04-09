import numpy as np
import cv2 as cv

# === Calibration & Settings ===
video_file = 'chessboard.mov'
K = np.array([[887.66457342, 0, 959.47532409],
              [0, 893.84894272, 522.79319593],
              [0, 0, 1]], dtype=np.float32)
dist_coeff = np.array([0.02874492, -0.05810351, -0.00472185, -0.00033239, 0.07060768], dtype=np.float32)
board_pattern = (10, 7)
board_cellsize = 0.025
board_criteria = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK

# === Chessboard 3D object points ===
obj_points = board_cellsize * np.array([[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])])

# === Open video ===
video = cv.VideoCapture(video_file)
assert video.isOpened(), 'Cannot read the given input, ' + video_file

while True:
    valid, img = video.read()
    if not valid:
        break

    # === Find chessboard corners ===
    success, img_points = cv.findChessboardCorners(img, board_pattern, board_criteria)
    if success:
        ret, rvec, tvec = cv.solvePnP(obj_points, img_points, K, dist_coeff)

        # === 피라미드 도형 정의 ===
        base_point = np.array([5 * board_cellsize, 3 * board_cellsize, 0.0])
        pyramid_size = 0.05  # 한 변 길이 (5cm)
        half = pyramid_size / 2

        # 꼭짓점 좌표 (4개 바닥 + 1개 꼭대기)
        pyramid_points = np.array([
            [-half, -half, 0], [half, -half, 0], [half, half, 0], [-half, half, 0],  # 바닥
            [0, 0, -pyramid_size]  # 꼭대기
        ]) + base_point

        # 투영
        pyramid_2d, _ = cv.projectPoints(pyramid_points, rvec, tvec, K, dist_coeff)
        pyramid_2d = np.int32(pyramid_2d).reshape(-1, 2)

        # 바닥 사각형 그리기
        cv.polylines(img, [pyramid_2d[:4]], True, (0, 255, 255), 2)

        # 바닥과 꼭대기 연결선
        for i in range(4):
            cv.line(img, pyramid_2d[i], pyramid_2d[4], (255, 100, 100), 2)

        # 카메라 위치 표시
        R, _ = cv.Rodrigues(rvec)
        p = (-R.T @ tvec).flatten()
        info = f'XYZ: [{p[0]:.3f} {p[1]:.3f} {p[2]:.3f}]'
        cv.putText(img, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))

    # 화면 출력 및 키 이벤트
    cv.imshow('Pose Estimation with Pyramid', img)
    key = cv.waitKey(10)
    if key == ord(' '):
        key = cv.waitKey()
    if key == 27:  # ESC
        break

video.release()
cv.destroyAllWindows()
