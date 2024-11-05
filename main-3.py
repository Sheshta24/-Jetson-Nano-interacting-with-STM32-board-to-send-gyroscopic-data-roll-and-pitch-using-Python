import time
import stm32_conn as connection
import onboard_comm as onboard

def main():
    ## Establish communication links with stm32.
    stm32 = connection.stm32_conn(port_name="/dev/ttyACM0")
    stm32.begin()

    # implement the STM32F3Discovery LED class
    led = onboard.LED()

    # Set up the STM32F3Discovery gyroscope class
    gyro = onboard.gyros()

    ## Toggle all LEDs on and off to demonstrate system readiness
    print("Triggering LEDs")

    for i in range(8):
        # Retrieve the LED command to illuminate the selected LED, then send a request to the STM32
        stm32.request(led.payload(i),sleep_time=0)
        time.sleep(0.1)

    stm32.request(led.payload(0),sleep_time=0)

    print("System started\n")

    ## Main User Control Menu
    while True:
        user_input = input("1. Start\n2. Calibrate\nE. Exit\nChoose (1/2/E): ").lower()
        
        # The subsequent process will continuously fetch gyroscopic data and refresh the LED to reflect the tilt orientation.
        if user_input == "1":
            
            print("System start. Press 'CTRL + C' to interrupt.")
            
            gyro.monitor_gyro(stm32.request)

        # Given the variability in sensitivity across different gyroscopes, the upcoming steps are designed to adjust the threshold for tilt detection within the system.
        elif user_input == "2":
            print("Calibrating")
            gyro.calibration(stm32)

        # The user opt to terminate the input process.
        elif user_input == "3":
            print("Exiting")
            break
        # Validation to handle potential user input errors.
        else:
            print("Kindly select your desired option..")
        print("\n")

    # close port connection
    stm32.close()

if __name__ == "__main__":
    main()
