import serial
import time
from pathlib import Path

# USB communication class for managing connections with the STM32F3Discovery board.
class stm32_conn:
    
    # Retrieve and set up the required port information.
    def __init__(self,path_name="/dev", port_begin="ttyA*", port_name="", baud_rate=9600,timeout=1):
        self.ports_path = Path(path_name)
        self.port_list = [str(port) for port in self.ports_path.glob(port_begin)]
        self.port_name = port_name
        self.port_setup(port_name=port_name)
        self.baud_rate = baud_rate
        self.time_out = timeout  
        #return
        #In Python, the initialization method __init__ must not explicitly return a value. Including a return statement at the conclusion of your __init__ function is superfluous.
    
    # Configuring the connection between the Jetson Nano and the STM32F3Discovery board.
    def port_setup(self, port_name = ""):
        
    #Verify the existence of a specified custom port name and, if found, update the port identifier accordingly (e.g., ttyACM0).
        if port_name and self.port_available(port_name=port_name):
            self.port_name = port_name
        elif not port_name:
            # If no port name is specified, select and configure a suitable one from the list of available ports.
            if self.port_list:
                for ind, prt in enumerate(self.port_list):
                    print(f"{ind + 1}. {prt}")
                # Get user to select a port of all the available ports
                try:
                    user_input = int(input("Choose an option listed above: ")) - 1
                    self.port_name = self.port_list[user_input]
                    print(f"Successfully connected to {self.port_name}.\n")
                except ValueError:
                    print(f"Enter a number from 1 to {len(self.port_list)}:")
                except IndexError:
                    print(f"Enter a valid option number (1 to {len(self.port_list)}):")
            else:
                print("Ensure the USB is properly connected.\n")
        else:
            print(f"{port_name} is not available.")

        return
    
    
    # This process will compare the provided or stored port name against the list of currently connected ports to verify if the specified port exists. 
    def port_available(self,port_name=""):
    
        # Raise an exception if no ports are found to be open.
        if not self.port_list:
            raise Exception("No USB connection found")

        # If stored or given port name is available, return True
        return self.port_name in self.port_list or port_name in self.port_list
    
    # Establish a connection between the device and the STM32F3Discovery
    def begin(self):
        if self.port_available():
            try:
                
                # Set up a connection
                self.stm32 = serial.Serial(self.port_name, self.baud_rate, timeout=self.time_out)
                return True
            
            # In case of encountering any errors, proceed with the following steps.
            except Exception as e:
                error = str(e)
                
                #If the error encountered is recognized as a common issue, provide a troubleshooting solution to address it.
                if error == "Access to /dev/ttyACM0 is denied. Check if you have the necessary permissions.":
                    raise Exception (f"In the terminal, apply this command to update permissions: 'sudo chmod 666 {self.port_name}'")
                    return False
        # If the port name attempted to connect doesnt exist, let user know connection wasnt successful
        else:
            print("Could not create a connection.")
        return False
    
    # Transmit data from device 
    def request(self,packet,sleep_time = 0.1):
        
        # Attempt 5 times to transmit and recieve acknowledgement
        for i in range(5):
            
            # Transmit the given data
            self.stm32.write(packet)
            time.sleep(sleep_time)
            
            # Read the return message
            data = self.stm32.readline().decode("utf-8")
            time.sleep(sleep_time)
            
            # Check if the return message has acknowledgement
            if ("OK" in data):
                return data
            elif ("x:" in data):
                return data
        return
    
    # Close the open stm32 connection
    def close(self):
        self.stm32.close()
        return

