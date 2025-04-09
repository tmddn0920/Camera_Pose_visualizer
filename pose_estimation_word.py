import numpy as np
import cv2 as cv

video_file = 'chessboard.mov'
K = np.array([[887.66457342, 0, 959.47532409],
              [0, 893.84894272, 522.79319593],
              [0, 0, 1]], dtype=np.float32)
dist_coeff = np.array([0.02874492, -0.05810351, -0.00472185, -0.00033239, 0.07060768], dtype=np.float32)
board_pattern = (10, 7)
board_cellsize = 0.025
board_criteria = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FAST_CHECK

obj_points = board_cellsize * np.array([[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])])

video = cv.VideoCapture(video_file)
assert video.isOpened(), 'Cannot read the given input, ' + video_file

while True:
    valid, img = video.read()
    if not valid:
        break

    success, img_points = cv.findChessboardCorners(img, board_pattern, board_criteria)
    if success:
        ret, rvec, tvec = cv.solvePnP(obj_points, img_points, K, dist_coeff)

        text_3d = np.array([[5 * board_cellsize, 3 * board_cellsize, 0.02]]) 
        text_2d, _ = cv.projectPoints(text_3d, rvec, tvec, K, dist_coeff)
        pt = tuple(np.int32(text_2d[0].ravel()))
        cv.putText(img, 'Seung Rain', pt, cv.FONT_HERSHEY_SIMPLEX, 2.0, (255, 100, 100), 3, cv.LINE_AA)

        R, _ = cv.Rodrigues(rvec)
        p = (-R.T @ tvec).flatten()
        info = f'XYZ: [{p[0]:.3f} {p[1]:.3f} {p[2]:.3f}]'
        cv.putText(img, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))

    cv.imshow('Pose Estimation with AR Text', img)
    key = cv.waitKey(10)
    if key == ord(' '):
        key = cv.waitKey()
    if key == 27:  # ESC
        break

video.release()
cv.destroyAllWindows()
