def _main():
    try:
        robot = rb.Cobot(ROBOT_IP)
        rc = rb.ResponseCollector()

        robot.set_operation_mode(rc, rb.OperationMode.Simulation)
        robot.set_speed_bar(rc, 0.5)


        # 티칭모드 활성화
        [res, pnt] = robot.set_freedrive_mode(rc, True)

        [res, pnt] = robot.set_freedrive_mode(rc, False)


        robot.flush(rc)
        rc = rc.error().throw_if_not_empty()
    except Exception as e:
        print(e)
    finally:
        print('Exit')


if __name__ == "__main__":
    _main()