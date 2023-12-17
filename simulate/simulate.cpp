#include <systemc>
using namespace sc_core;

SC_MODULE(ROLLERCOASTER) {
  // variable decleration
  sc_event proximitySensorEvent;
  sc_event controllerEvent;
  double maxSpeed;     // Tốc độ tối đa
  double minSpeed;     // Tốc độ tối thiểu
  int maxPwmWidth;  // Độ rộng xung tối đa
  int minPwmWidth;  // Độ rộng xung tối thiểu
  
  int pulse;
  double speed;
  int caseTrack;


  // check isRun
  int isRunTrack1;
  int isRunTrack2;



  SC_CTOR(ROLLERCOASTER) {
    SC_THREAD(speed_sensor);
    SC_THREAD(controller);
    SC_THREAD(proximity_sensor);
  }

  // void trigger() {
  //   while (true) {
  //     e.notify(1, SC_SEC);

  //     wait(3, SC_SEC);
  //   }
  // }
  // void catcher() {
  //   while (true) {
  //     wait(e);
  //     std::cout << "Event cateched at " << sc_time_stamp() << std::endl;
  //   }
  // }

  void controller() {
    while (true) {
      wait(proximitySensorEvent);
      
      if(caseTrack == 1 && isRunTrack1 == 0) {
        std::cout << "You are in track 1 " << sc_time_stamp() << std::endl;
        std::cout << "The required speed is: 70.5";
        pulse = 200;
        controllerEvent.notify(1, SC_SEC);
        isRunTrack1 = 1;
      }
      if(caseTrack == 2 && isRunTrack2 == 0) {
        std::cout << "You are in track 2 " << sc_time_stamp() << std::endl;
        std::cout << "The required speed is: 44.5";
         controllerEvent.notify(1, SC_SEC);
         isRunTrack2 = 1;
      }
    }
  }


  void speed_sensor() {
    while (true) {
      wait(controllerEvent);
      speed = (pulse * (maxSpeed - minSpeed) ) / (maxPwmWidth - minPwmWidth);
      if(caseTrack == 1) {
        while(speed < 70.5) {
          std::cout << "The pulse:  "<< pulse << "\t" << "The speed: " << speed <<"\t" << sc_time_stamp() << std::endl;
          pulse += 100;
          speed = (pulse * (maxSpeed - minSpeed) ) / (maxPwmWidth - minPwmWidth);
          wait(2, SC_SEC);
        }
          std::cout << "The pulse:  "<< pulse << "\t" << "The speed: " << speed <<"\t" << sc_time_stamp() << std::endl;
      }
      if(caseTrack == 2) {
        while(speed > 44.5) {
          std::cout << "The pulse:  "<< pulse << "\t" << "The speed: " << speed <<"\t" << sc_time_stamp() << std::endl;
          pulse -= 50;
          speed = (pulse * (maxSpeed - minSpeed) ) / (maxPwmWidth - minPwmWidth);
          wait(2, SC_SEC);
        }
          std::cout << "The pulse:  "<< pulse << "\t" << "The speed: " << speed <<"\t" << sc_time_stamp() << std::endl;
      }

    }
  }

  void proximity_sensor() {
    caseTrack = 1;
    isRunTrack1 = 0;
    proximitySensorEvent.notify(1, SC_SEC);
    wait(40, SC_SEC);
    caseTrack = 2;
    isRunTrack2 = 0;
    proximitySensorEvent.notify(1, SC_SEC);
  }






};
	
int sc_main(int, char*[]) {
  // initialize
  std::cout<< "Roller Coaster 20231 - by xxxxxx\n";
  std::cout<< "The weight: 1500kg\n";
  std::cout<< "Some information .....\n";



  ROLLERCOASTER rollercoaster("ROLLERCOASTER");
  rollercoaster.minSpeed = 0;
  rollercoaster.maxSpeed = 100;
  rollercoaster.minPwmWidth = 100;
  rollercoaster.maxPwmWidth = 2500;
  rollercoaster.caseTrack = 0;


  sc_start(150, SC_SEC);
  return 0;

}