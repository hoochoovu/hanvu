import pycuda.driver as cuda
import pycuda.autoinit

def list_gpus():
    device_count = cuda.Device.count()
    
    print("Available GPUs:")
    for i in range(device_count):
        device = cuda.Device(i)
        print(f"GPU ID: {i}, Name: {device.name()}, Total Memory: {device.total_memory() / 1024**2:.2f} MB")

if __name__ == "__main__":
    list_gpus()