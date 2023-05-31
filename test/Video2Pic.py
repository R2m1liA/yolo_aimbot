import cv2


def Video2Pic(videoPath, timeF):
    cap = cv2.VideoCapture(videoPath)
    cntF = 1
    cnt = 1

    if cap.isOpened():
        rval, frame = cap.read()
    else:
        rval = False

    while rval:
        rval, frame = cap.read()
        if (cntF % timeF == 0):
            cv2.imwrite('./pic3/' + str(cnt) + '.jpg', frame)
            print('Frame ' + str(cntF) + ' saved as ' + str(cnt) + '.jpg')
            cnt += 1
        cntF += 1
    cap.release()

Video2Pic('video/2023-05-09 19-18-11.mkv', 60)
