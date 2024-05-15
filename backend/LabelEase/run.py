import os

def main():
    print("start...")
    os.system("python preprocess.py")
    os.system("python statistic.py")
    os.system("python generate_trace_tuple.py")
    os.system("python trainer.py")
    os.system("python generate_vector.py")
    os.system("python cluster.py")
    print("end...")

if __name__ == '__main__':
    main()