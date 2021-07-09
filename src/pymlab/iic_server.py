import sys
from pymlab.sensors.iic import load_driver

def main():
    tru_stdout = sys.stdout; sys.stdout = sys.stderr
    def read_msg():
        try:
            m = eval(input())
        except EOFError:
            sys.exit(0)
        if not isinstance(m, tuple) or len(m) == 0:
            raise RuntimeError('received invalid message ' + repr(m))
        return m[0], m[1:]
    def write_msg(m):
        tru_stdout.write(repr(m) + '\n')
        tru_stdout.flush()
    try:
        method, args = read_msg()
        assert method == "load_driver"
        d = load_driver(**args[0])
    except Exception as e:
        write_msg({'good': False, 'exception': str(e)})
        sys.exit(1)
    write_msg({'good': True, 'result': None})
    while True:
        method, args = read_msg()
        try:
            res = getattr(d, method)(*args)
        except Exception as e:
            write_msg({'good': False, 'exception': str(e)})
        else:
            write_msg({'good': True, 'result': res})

if __name__ == "__main__":
    main()
