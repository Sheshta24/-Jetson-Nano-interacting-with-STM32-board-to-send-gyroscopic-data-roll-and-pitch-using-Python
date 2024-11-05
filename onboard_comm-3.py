import time

# An led class handler
class LED:
    
    #Initial system
    def __init__(self):
        # Led pins references
        self.led_pins = tuple(list(range(8)))
        return
    
    # Generate the required command to activate a specified LED pin.
    def payload(self, led_pin):
        if led_pin<len(self.led_pins) and led_pin>=0:

            data = bytearray()
            data.append(0x01)
            data.append(led_pin)

        return data
    
# A gyroscope class handler
class gyros:
    
    # Set up gyroscope sensitivity parameters and other related information upon initialization.
    def __init__(self,x_max = 65000, x_min = -52535, y_max = 65000, y_min = -65000):
        
        # Gyro sensitivity data
        self.x_max, self.x_min = x_max, x_min
        self.y_max, self.y_min = y_max, y_min
        
        # Gyroscope tilt signaling, where False denotes the most recent or current direction of tilt.
        self.x_max_state = self.x_min_state = self.y_max_state = self.y_min_state = True

        return
    
    # Collect sensitivity measurements within a specified duration (t).
    def read_data(self, obj, txt, init_time = 3):
        x=[]
        y=[]
        
        # Pause until the user initiates the data collection process.
        input(f"Press Enter to begin, then tilt {txt}.")
        start_time = time.time()

        while init_time - (time.time()-start_time)>0:

            print(f"Adjust angle {txt}. Time left: \t {init_time - (time.time()-start_time)} seconds.")
            data = str(obj.write(self.payload()))
            data = data.split(":")[1:]
            x_data = float(data[0].split(",")[0])
            y_data = float(data[1].split("\n")[0])
            x.append(abs(x_data))
            y.append(abs(y_data))

        print(x)
        print(y)

        return max(x),max(y)
    
    #Calibrator to calibrate the sensitivity data
    def calibration(self,obj):
        
        # An interactive loop allowing the user to select which sensitivity data, roll or pitch, to adjust.
        while True:
            user_input = input("\n1. Set lower X limit ({})\t(for counter-clockwise pitch)"
                   "\n2. Set upper X limit ({})\t(for clockwise pitch)"
                   "\n3. Set lower Y limit ({})\t(for counter-clockwise roll)"
                   "\n4. Set upper Y limit ({})\t(for clockwise roll)"
                   "\nB. Back to the main menu."
                   "\nSelect Option (1/2/3/4/B): ".format(self.x_min, self.x_max, self.y_min, self.y_max)).lower()
            
            if user_input == "1":
                self.x_min = -self.read_data(obj, "Anti-clockwise along the x-axis")[0]
            elif user_input == "2":
                self.x_max = self.read_data(obj, "Clockwise along the x-axis")[0]
            elif user_input == "3":
                self.y_min = -self.read_data(obj, "Anti-clockwise along the y-axis")[1]
            elif user_input == "4":
                self.y_max = self.read_data(obj, "Clockwise along the y-axis")[1]
            elif user_input == "b":
                break
            else:
                print("Please choose your preferred option.")
        return
    
    # Reset all gyro tilt indication
    def reset(self):
        self.x_max_state = self.x_min_state = self.y_max_state = self.y_min_state = True
    
    # Create a command to be sent to the STM32F3Discovery, requesting the gyroscope measurements.
    def payload(self):
        return bytearray([0x02])

        
    def monitor_gyro(self, request_fn):
        led = LED()
        try:
            while True:
                data = str(request_fn(self.payload(), sleep_time=0)).split(":")[1:]

                if len(data) > 1:
                    x_gyro, y_gyro = map(lambda d: float(d.split(",")[0]), data[:2])

                    conditions = [(x_gyro > self.x_max and self.x_max_state, 0, False),
                                (x_gyro < self.x_min and self.x_min_state, 4, False),
                                (y_gyro > self.y_max and self.y_max_state, 6, False),
                                (y_gyro < self.y_min and self.y_min_state, 2, False)]
                    
                    for condition, led_code, state in conditions:
                        if condition:
                            request_fn(led.payload(led_code), sleep_time=0.1)
                            self.reset()
                            setattr(self, '_'.join(['x_max_state', 'x_min_state', 'y_max_state', 'y_min_state'][led_code // 2]), state)
                            break

        except KeyboardInterrupt:
            print("Back to the main menu.")
