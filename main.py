import threading
import time
import unittest
from car import Car
from car_controller import CarController
from gui import CarSimulatorGUI

MAX_SPEED = 140 # 최대 시속
LOCK_SPEED = 30 # 차량잠금 시속
AUTO_LOCKING_FLAG = True



# execute_command를 제어하는 콜백 함수
# -> 이 함수에서 시그널을 입력받고 처리하는 로직을 구성하면, 알아서 GUI에 연동이 됩니다.
def execute_command_callback(command, car_controller):
    global AUTO_LOCKING_FLAG
    
    def all_door_closed(car_controller):            #모든 문이 닫혀 있다면
        return car_controller.get_left_door_status()=="CLOSED" and car_controller.get_right_door_status()=="CLOSED"

    def all_door_locked(car_controller):            #모든 문이 잠겨 있다면
        return car_controller.get_left_door_lock()=="LOCKED" and car_controller.get_right_door_lock()=="LOCKED"

    def all_door_lock(car_controller):              #모든 문 잠금
        car_controller.lock_left_door()
        car_controller.lock_right_door()
    
    def all_door_unlock(car_controller):            #모든 문 잠금해제
        car_controller.unlock_left_door()
        car_controller.unlock_right_door()



    if command == "ENGINE_BTN":
        if car_controller.get_speed()==0: # 시속이 0일 경우에 한해서 버튼 토글 가능
            car_controller.toggle_engine() # 시동 ON / OFF
        
    elif command == "ACCELERATE":
        if (car_controller.get_trunk_status()  #trunk_status True = closed 트렁크가 닫혀 있어야 함
            and all_door_closed(car_controller) #모든 문이 닫혀 있어야 함
            and car_controller.get_speed()<MAX_SPEED): # 최대 시속이라면 무시
                car_controller.accelerate() # 속도 +10
                if(AUTO_LOCKING_FLAG): # 처음 30km/h에 도달했을 시
                    if car_controller.get_speed()==LOCK_SPEED: # 차량잠금 시속에 도달하면
                        all_door_lock(car_controller)        # 차량을 양쪽문 잠김
                        car_controller.lock_vehicle()        # 차량의 잠금 상태 = true
                        AUTO_LOCKING_FLAG = False

    elif command == "BRAKE":
        car_controller.brake() # 속도 -10
        if(car_controller.get_speed() < 30):
            if(AUTO_LOCKING_FLAG == False):
                AUTO_LOCKING_FLAG = True
            
        
    elif command == "LOCK":
        if all_door_closed(car_controller): #모든 문이 닫혀 있을 떄만 동작
            all_door_lock(car_controller) # 양쪽 문 잠금
            car_controller.lock_vehicle() # 차량의 잠금 상태 = true

    elif command == "UNLOCK":
        if(car_controller.get_speed()<LOCK_SPEED # 차량잠금 시속 보다 차량의 시속이 느려야함
            and all_door_closed(car_controller)): #모든 문이 닫혀 있을 떄만 동작
                all_door_unlock(car_controller) # 양쪽 문 잠금해제
                car_controller.unlock_vehicle() # 차량의 잠금 상태 = false

    elif command == "LEFT_DOOR_LOCK":
        if car_controller.get_left_door_status()=="CLOSED":
            car_controller.lock_left_door() # 왼쪽문 잠금
            if all_door_locked(car_controller): # 차량의 모든 문이 잠겨있다면
                car_controller.lock_vehicle()   # 차량의 잠금 상태 = true
    elif command == "RIGHT_DOOR_LOCK":
        if car_controller.get_right_door_status() == "CLOSED":
            car_controller.lock_right_door()  # 오른쪽문 잠금
            if all_door_locked(car_controller):  # 차량의 모든 문이 잠겨있다면
                car_controller.lock_vehicle()  # 차량의 잠금 상태 = true

    elif command == "LEFT_DOOR_UNLOCK":
        if car_controller.get_speed()<LOCK_SPEED: # 차량잠김 시속 보다 차량의 시속이 느려야함
            car_controller.unlock_left_door() # 왼쪽문 잠금해제
            car_controller.unlock_vehicle()  # 차량의 잠금 상태 = false
    elif command == "RIGHT_DOOR_UNLOCK":
        if car_controller.get_speed() < LOCK_SPEED: # 차량잠김 시속 보다 차량의 시속이 느려야함
            car_controller.unlock_right_door()  # 오른쪽문 잠금해제
            car_controller.unlock_vehicle()  # 차량의 잠금 상태 = false

    elif command == "LEFT_DOOR_OPEN":
        if(car_controller.get_left_door_lock()=="UNLOCKED" # 왼쪽 문이 잠겨있지 않아야 하고
            and car_controller.get_speed()==0): # 차량의 시속이 0이어야한다.
                car_controller.open_left_door() # 왼쪽문 열기
    elif command == "RIGHT_DOOR_OPEN":
        if (car_controller.get_right_door_lock() == "UNLOCKED" # 오른쪽 문이 잠겨있지 않아야 하고
            and car_controller.get_speed() == 0): # 차량의 시속이 0이어야한다.
                car_controller.open_right_door()  # 오른쪽문 열기

    elif command == "LEFT_DOOR_CLOSE":
        car_controller.close_left_door() # 왼쪽문 닫기
    elif command == "RIGHT_DOOR_CLOSE":
        car_controller.close_right_door() # 오른쪽문 닫기

    elif command == "TRUNK_OPEN":
        if car_controller.get_speed()==0: #차량의 시속이 0이어야한다.
            car_controller.open_trunk() # 트렁크 열기

    elif command == "TRUNK_CLOSE":
        car_controller.close_trunk() #트렁크 닫기

    elif command == "SOS":              #---SOS 기능---
        if car.speed == 0: # 정지상태에서 SOS 기능 사용시.
            car_controller.unlock_vehicle()
            car_controller.unlock_left_door()
            car_controller.unlock_right_door()
            car_controller.open_trunk()         
        while car.speed > 0:            #차가 정지상태가 아닌 동안
            car_controller.brake()
            gui.update_gui()
            time.sleep(0.1)             #시간함수를 통해 속도가 줄어듦을 시각적으로 표현
            if car.speed == 0:          #모두 줄어들었을 때
                car_controller.unlock_vehicle()
                car_controller.unlock_left_door()
                car_controller.unlock_right_door()
                car_controller.open_trunk()        
                break   
    


def restatus():          #초기 상태로 초기화
    while car.speed>0:
        car_controller.brake()
    car_controller.close_trunk()
    car_controller.close_right_door()
    car_controller.close_left_door
    car_controller.lock_right_door()
    car_controller.lock_left_door()
    if car.engine_on == True:
        car_controller.toggle_engine()
    gui.update_gui()

# SOS unittest 
class Test_SOS_system(unittest.TestCase):
   
    def test_sos_zero(self):                    #SOS사용시 시속 테스트
       restatus()
       car_controller.toggle_engine()           #시속이 0일 때 SOS 사용
       execute_command_callback("SOS",car_controller)
       SOS_speed = car_controller.get_speed()
       self.assertEqual(SOS_speed,0)            

       restatus()                               #시속이 10이상일 때 SOS 사용
       car_controller.accelerate()              
       execute_command_callback("SOS",car_controller)
       SOS_speed = car_controller.get_speed()
       self.assertEqual(SOS_speed,0)            

    def test_sos_opentrunk(self):                   #SOS사용시 트렁크 상태 체크
        restatus()
        car_controller.toggle_engine()
        execute_command_callback("SOS",car_controller)
        trunkstat = car_controller.get_trunk_status()
        self.assertFalse(trunkstat)                 #트렁크는 False=Opened

    def test_sos_unlockdoor(self):              #SOS 사용시 차량 문 잠금상태 확인
        restatus()
        car_controller.toggle_engine()
        execute_command_callback("SOS",car_controller)
        leftD = car_controller.get_left_door_lock()
        rihgtD = car_controller.get_right_door_lock()
        getlock= car_controller.get_lock_status()
        self.assertEqual(leftD,"UNLOCKED")
        self.assertEqual(rihgtD,"UNLOCKED")
        self.assertFalse(getlock)
        


# 파일 경로를 입력받는 함수
# -> 가급적 수정하지 마세요.
#    테스트의 완전 자동화 등을 위한 추가 개선시에만 일부 수정이용하시면 됩니다. (성적 반영 X)
def file_input_thread(gui):
    while True:
        file_path = input("Please enter the command file path (or 'exit' to quit): ")

        if file_path.lower() == 'exit':
            print("Exiting program.")
            break

        # 파일 경로를 받은 후 GUI의 mainloop에서 실행할 수 있도록 큐에 넣음
        gui.window.after(0, lambda: gui.process_commands(file_path))

# 메인 실행
# -> 가급적 main login은 수정하지 마세요.
if __name__ == "__main__":
    car = Car()
    car_controller = CarController(car)


    # GUI는 메인 스레드에서 실행
    gui = CarSimulatorGUI(car_controller, lambda command: execute_command_callback(command, car_controller))

    # 파일 입력 스레드는 별도로 실행하여, GUI와 병행 처리
    input_thread = threading.Thread(target=file_input_thread, args=(gui,))
    input_thread.daemon = True  # 메인 스레드가 종료되면 서브 스레드도 종료되도록 설정
    input_thread.start()

    suite=unittest.TestSuite()  #suite로 unittest 관리
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_SOS_system))
    unittest.TextTestRunner().run(suite)
    restatus()

    # GUI 시작 (메인 스레드에서 실행)
    gui.start()