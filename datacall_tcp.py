# tcp 정보 불러오는 코드

import rbpodo as rb


def _main():
    data_channel = rb.CobotData("192.168.0.100")
    data = data_channel.request_data(1.0)
    print(data.sdata.tcp_ref)


if __name__ == "__main__":
    _main()
